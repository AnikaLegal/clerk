#/bin/bash
# Create a checksum to help us cache our docker images in CircleCI
# Checksum is written to .checksum
echo "Getting MD5 checksum for files"
rm -f .checksum  # Shit gets weirdly recursive if you keep this around.

# Generate checksum for each file - exclude irrelvant files, build artifacts, etc
PROJECT_FILES_MD5=$(find . \
    -type f \
    -not -path "./.git/*" \
    -not -path "./scripts/*" \
    -not -path "./.circleci/*" \
    -not -path "./app/frontend/build/*" \
    -not -path "./app/frontend/node_modules/*" \
    -not -name "*.pyc" \
    -not -name ".gitignore" \
    -not -name "README.md" \
    -exec md5sum {} \;)

echo -e "$PROJECT_FILES_MD5"
echo "These files will be used for the project checksum"
PROJECT_CHECKSUM=$(echo "$PROJECT_FILES_MD5" | md5sum)
echo "Project checksum is $PROJECT_CHECKSUM"
echo "$PROJECT_CHECKSUM" > '.checksum'
