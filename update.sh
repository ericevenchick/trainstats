python generate_json.py
s3cmd del s3://www.trainstats.ca/data --recursive
s3cmd sync ./out/ s3://www.trainstats.ca/ --acl-public

