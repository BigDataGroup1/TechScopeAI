#!/bin/bash
# Quick script to check Cloud Run service URLs and CORS configuration

echo "=== CLOUD RUN SERVICE URLS ==="
echo ""

# Get URLs
FRONTEND_URL=$(gcloud run services describe techscopeai-web --region us-central1 --format='value(status.url)' 2>/dev/null)
BACKEND_URL=$(gcloud run services describe techscopeai-api --region us-central1 --format='value(status.url)' 2>/dev/null)

echo "Frontend Service:"
echo "  Name: techscopeai-web"
echo "  URL:  $FRONTEND_URL"
echo ""

echo "Backend Service:"
echo "  Name: techscopeai-api"
echo "  URL:  $BACKEND_URL"
echo ""

echo "=== CORS CONFIGURATION ==="
CORS_ORIGIN=$(gcloud run services describe techscopeai-api --region us-central1 --format='yaml(spec.template.spec.containers[0].env)' 2>/dev/null | grep -A 1 "ALLOWED_ORIGINS" | grep "value:" | awk '{print $2}')
echo "Backend ALLOWED_ORIGINS: $CORS_ORIGIN"
echo ""

# Check for mismatch
if [ "$FRONTEND_URL" != "$CORS_ORIGIN" ]; then
    echo "⚠️  MISMATCH DETECTED!"
    echo "   Service URL: $FRONTEND_URL"
    echo "   CORS Origin: $CORS_ORIGIN"
    echo ""
    echo "   To fix, run:"
    echo "   gcloud run services update techscopeai-api --region us-central1 \\"
    echo "     --update-env-vars ALLOWED_ORIGINS=\"$FRONTEND_URL\""
else
    echo "✅ CORS configuration matches service URL"
fi

echo ""
echo "=== TEST ENDPOINTS ==="
echo "Backend Health Check:"
curl -s "$BACKEND_URL/health" | head -3
echo ""
