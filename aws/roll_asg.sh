#!/bin/bash
set -euo pipefail

# Check that component, version, and namespace are provided
if [ $# -ne 3 ]; then
    echo "No component, version, or namespace specified. Usage: ./roll-asg.sh <component> <version> <namespace>"
    exit 1
fi

# Set variables
COMPONENT=$1
VERSION=$2
NAMESPACE=$3
ASG_NAME="${NAMESPACE}-${COMPONENT}-asg"
SSM_PARAMETER_NAME="/${NAMESPACE}/${COMPONENT}/version"

echo "Starting deployment of version $VERSION to $ASG_NAME..."

# Update SSM parameter
echo "Updating SSM parameter $SSM_PARAMETER_NAME to $VERSION..."
aws ssm put-parameter \
    --name "$SSM_PARAMETER_NAME" \
    --value "$VERSION" \
    --type String \
    --overwrite

# if ENV FORCE is set, cancel the previous instance refresh
if [ "${FORCE:-}" ]; then
    echo "Force flag provided, cancelling previous instance refresh..."
    aws autoscaling cancel-instance-refresh \
        --auto-scaling-group-name "$ASG_NAME"
    echo "Waiting 60 seconds for the instance refresh to cancel..."
    sleep 60
fi

# Start instance refresh
echo "Starting instance refresh..."
aws autoscaling start-instance-refresh \
    --auto-scaling-group-name "$ASG_NAME"

START_TIME=$(date +%s)
PRETTY_TIME=$(date +"%Y-%m-%d %H:%M:%S")
echo "${PRETTY_TIME}: Instance refresh started. Monitoring progress..."
echo "Console URL: https://us-east-2.console.aws.amazon.com/ec2/home?region=us-east-2#AutoScalingGroupDetails:id=prod-sun-asg;view=instanceRefresh"


# Monitor the refresh status
while true; do
    echo "----------------------------------------"
    echo ""
    REFRESH_STATUS=$(aws autoscaling describe-instance-refreshes \
        --auto-scaling-group-name "$ASG_NAME" \
        --query 'InstanceRefreshes[0].[Status, StatusReason,PercentageComplete]' \
        --output text)

    STATUS=$(echo "$REFRESH_STATUS" | cut -f1)
    REASON=$(echo "$REFRESH_STATUS" | cut -f2)
    PROGRESS=$(echo "$REFRESH_STATUS" | cut -f3)

    ELAPSED_TIME=$(( $(date +%s) - START_TIME ))
    PRETTY_TIME=$(date +"%Y-%m-%d %H:%M:%S")
    echo "${PRETTY_TIME} (${ELAPSED_TIME}s elapsed): Status: $STATUS | Progress: $PROGRESS% | Reason: $REASON"

    # Get instance statuses
    INSTANCES=$(aws autoscaling describe-auto-scaling-instances \
        --query "AutoScalingInstances[?AutoScalingGroupName=='$ASG_NAME'].[InstanceId,LifecycleState,LaunchTime,HealthStatus]" \
        --output text)

    echo "Current instances:"
    echo "$INSTANCES" | while read -r INSTANCE_ID STATE LAUNCH_TIME HEALTH_STATUS; do
        echo "  Instance $INSTANCE_ID: $STATE | Health: $HEALTH_STATUS | Launched: $LAUNCH_TIME"
    done

    case $STATUS in
        "Successful")
            echo "✅ Instance refresh completed successfully!"
            exit 0
            ;;
        "Failed"|"Cancelled")
            echo "❌ Instance refresh $STATUS: $REASON"
            exit 1
            ;;
        "Pending"|"InProgress")
            sleep 17
            ;;
        *)
            echo "❌ Unknown status: $STATUS"
            exit 1
            ;;
    esac
done
