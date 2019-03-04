#!/usr/bin/python36
import sys, os, argparse, json
from subprocess import DEVNULL, STDOUT, check_call, check_output

parser = argparse.ArgumentParser(description='Import images for disconnected OCP installs')
parser.add_argument('type', action="store", help='type of copy to perform, docker-daemon | docker | tarball, default is docker-daemon')
parser.add_argument('source', action="store", help='Ex: brew-pulp-docker01.web.prod.ext.phx2.redhat.com:8888')
parser.add_argument('dest', action="store", help='destination, Ex: 192.168.0.4:1234')
parser.add_argument('-d', action="store_true", default=False, help='debug mode')
parser.add_argument('-t', action="store", dest="tag", help="override the tag", default=False)
parser.add_argument('-a', action="store", dest="alias", help="set a tag alias", default=False)
parser.add_argument('-l', action="store", dest="list", help="image list, default is core_images.txt", default='core_images.txt')
args = parser.parse_args()

uri_string = False

if args.d: print("\n"+str(args)+"\n")

list = open(args.list).read().split()

if args.type == 'docker':
    uri_string = 'docker://%s'%(args.dest)
elif args.type == 'docker-daemon':
    uri_string = 'docker-daemon:%s'%(args.dest)
elif args.type == 'tarball':
    uri_string = 'tarball:%s'%(args.dest)
else:
    print("unknown type '%s'"%(args.type))

if uri_string:
    if args.d: print("- dest uri string is '%s'"%(uri_string))
else:
    print("\n ERROR: couldnt parse uri string")

if os.getuid() != 0: print("\n ERROR: root is required"); sys.exit(2)
try:
    check_call(['skopeo'], stdout=DEVNULL, stderr=DEVNULL)
except: 
    print("\n ERROR: skopeo is not installed"); sys.exit(3)

def parse_tag(image):
    try:
        (img, tag) = image.split(':')
    except:
        img = image
        tag = None
    if args.tag:
        tag = args.tag
    elif args.tag == '':
        tag = None
    if tag:
        image_string = img+':'+tag
    else:
        image_string = img
    return image_string

pass_list = []
# iterate over the list and verify they are accessible
for image in list:
    if image.startswith('#'):
        continue
    else:
        image_string = parse_tag(image)
    
    cmdline = ['skopeo', '--insecure-policy', 'inspect', '--tls-verify=false', "docker://%s/%s"%(args.source, image_string)]
    #if args.d: print('- '+' '.join(cmdline))

    try:
        json_data = json.loads(check_output(cmdline))
        version = json_data['Labels']['version']
        release = json_data['Labels']['release']
    except KeyboardInterrupt:
        print("\nbye..."); sys.exit(1)
    except:
         print("- failed to inspect docker://%s/%s"%(args.source, image_string))
    else:
        if args.d: print("- inspected %s/%s (%s-%s)"%(args.source, image_string, version, release))
        pass_list.append(image_string)

print("Starting to copy '%s' images"%(len(pass_list)))

# iterate over the pass list and copy the images
for image in pass_list:
    cmdline = ['skopeo', '--insecure-policy', 'copy', '--src-tls-verify=false', '--dest-tls-verify=false', "docker://%s/%s"%(args.source, image), "%s/%s"%(uri_string, image)]
    if args.d: print('- '+' '.join(cmdline))
    try:
        check_call(cmdline, stdout=DEVNULL, stderr=STDOUT)
    except KeyboardInterrupt:
        print("\nbye..."); sys.exit(1)
    except:
        print("- failed to save docker://%s/%s"%(args.dest, image))
    else:
        print("- saved %s/%s"%(uri_string, image))

    if args.alias:
        try:
            check_call(['skopeo', '--insecure-policy', 'copy', '--src-tls-verify=false', '--dest-tls-verify=false', "docker://%s/%s"%(args.source, image), "%s/%s"%(uri_string, image.split(':')[0]+':'+args.alias)], stdout=DEVNULL, stderr=STDOUT)
        except KeyboardInterrupt:
            print("\nbye..."); sys.exit(1)
        else:
            print("  + added tag alias '%s'"%(args.alias))
 