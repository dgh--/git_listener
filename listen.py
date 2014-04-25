#!venv/bin/python
 
# Flask is installed in a virtualenv, so WSGI requires
# us to use execfile to activate it:
 
activate_this = 'venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
 
from flask import Flask, request
import json, urllib2, os
 
app = Flask(__name__)
 
@app.route('/post', methods=['POST'])
def receive_ping():
  request_object = request.get_json()
  # request.get_json() yields a dictionary object;
  # now we retrieve username, reponame, and sha checksum
  # from the payload like so:
  owner = request_object["commits"][0]["author"]["username"]
  if owner != "dgh--":
    return "User not authorised"
  repo  = request_object["repository"]["name"]
  sha   = request_object["commits"][0]["id"]
  #www_sites_folder = '' # set this to wherever you tend to keep your sites
  www_sites_folder = '/home/www-data/git-deployed-sites'
  # construct URL for querying that the commit referred to in the payload exists:
  # further reading on GitHub Commit API: https://developer.github.com/v3/repos/commits/
  url   = "https://api.github.com/repos/{0}/{1}/commits/{2}".format(owner, repo, sha)
 
  # you'll also want to check whether
  # request_object["ref"] == "refs/heads/master"
  # (assuming that you only want to deploy changes to master)
  if request_object["ref"] != "refs/heads/master":
    # not a commit to master branch, ignore
    return "Not a commit to master branch"
 
  # query above URL, check that we have matching checksums;
  # if checksums don't match, go no further
  response = urllib2.urlopen(url)
  request_object2 = json.loads(response.read())
  if sha != request_object2["sha"]:
    return "COMPUTER SAYS NO"
 
 
 
  # URL for zip will be of the form  
  # https://github.com/<username>/<reponame>/archive/master.zip
  # We use wget, unzip and cp to download, decompress 
  # and copy the code to its intended destination..
 
  zip_url = "https://github.com/{0}/{1}/archive/master.zip".format(owner, repo)
  cmd = "wget --no-check-certificate {0}".format(zip_url)
  os.system(cmd)
 
  os.system("unzip master.zip")
  cmd = "cp -R {0}-master/* {1}/{0}/".format(repo, www_sites_folder)
  os.system(cmd)
 
  # cleanup: remove any previous downloaded files;
  # (anything from Github has "master" in its name)
  os.system('rm -r *master*')
 
  return "OK"
 
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
