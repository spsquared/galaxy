#!/bin/bash

# Can't run the script? You may need to run `chmod +x generate_types.sh` to make this script executable.
# This script should be run from the frontend folder.

# Exit the script if an error occurs
set -e

echo "Running generate_types.sh"

cd ../backend

echo "Generating OpenAPI 3.0 backend schema from siarnaq.."
# `conda run -n galaxy` runs the command inside the conda environment.
conda run -n galaxy python manage.py spectacular --file ../frontend/schema.yml --validate

cd ../frontend

# Delete the types folder before regenerating it.
echo "Deleting the old types folder.."
rm -rf ./src/api/_autogen

# Generate types folder
echo "Generating typescript types from schema, placing them in frontend/src/api/_autogen.."
mkdir src/api/_autogen
conda run -n galaxy npx @openapitools/openapi-generator-cli generate -i schema.yml -o src/api/_autogen -g typescript-fetch --additional-properties=modelPropertyNaming=original --additional-properties=disallowAdditionalPropertiesIfNotPresent=false --additional-properties=stringEnums=true
