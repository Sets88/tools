usage() {
    echo "Site downloader\nUsage $0 <URL>"
    exit 1
}

if [ -z "$1" ]; then
    usage
fi

domain=`echo $1 awk -F/ '{print $3}'`

if [ -z "$domain" ]; then
    usage
fi

wget \
     --recursive \
     --no-clobber \
     --page-requisites \
     --html-extension \
     --convert-links \
     --restrict-file-names=windows \
     --domains $domain \
     --no-parent \
         $1