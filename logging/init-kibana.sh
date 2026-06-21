#!/bin/bash
echo "Waiting for Kibana to be ready..."
# Keep looping until Kibana status API returns a valid HTTP response
until curl -s http://kibana:5601/api/status | grep -q "ui" || curl -s http://kibana:5601/status | grep -q "kbn-status" || curl -s -I http://kibana:5601/ | grep -q "200"; do
  sleep 3
done
echo "Kibana is up! Creating index pattern/data view..."
curl -s -X POST "http://kibana:5601/api/data_views/data_view" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{"data_view": {"title": "polaris-logs-*", "name": "Polaris Logs", "timeFieldName": "timestamp"}}'
echo "Kibana data view created successfully!"
