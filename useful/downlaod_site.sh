if [ -z $1 ]; then
    echo "Site downloader\nUsage $0 <URL>"
    exit 1
fi
wget \
     --recursive \
     --no-clobber \
     --page-requisites \
     --html-extension \
     --convert-links \
     --restrict-file-names=windows \
     --domains $1 \
     --no-parent \
         $1