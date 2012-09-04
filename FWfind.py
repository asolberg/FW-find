import sys, re
import urllib
import operator
def sort_table(table, cols):
    for col in reversed(cols):
        if col == 0:
            table = sorted(table, key=operator.itemgetter(col), reverse=True)
        else:
            table = sorted(table, key=operator.itemgetter(col))
    return table

def SendGmail(message):
    import smtplib  
    import datetime

    date_fmt = '%Y-%m-%d'
    fromaddr = 'sandybridge@do-not-reply.com'  
    toaddrs  = 'asolberg@gmail.com'  
    msg = message
    subj = 'FW Harvester Results ' + datetime.datetime.now().strftime(date_fmt)
    
    
    # Credentials (if needed)  
    username = 'asolberg'  
    password = 'ntabbhhnrfyh'  
  
    # The actual mail send  
    server = smtplib.SMTP('smtp.gmail.com:587')  
    server.starttls()  
    server.login(username,password)
    sendmsg = "From: %s\nTo: %s\nSubject: %s\n\n%s" % ( fromaddr, toaddrs, subj, msg )
    server.sendmail(fromaddr, toaddrs, sendmsg)  
    server.quit()

def FWFind(num_pages=20, age_cutoff=2, rating_cutoff=15):
    print 'Welcome to the FatWallet Forum harvester.\nProcessing.....'
    contents = ''
    all_pat = re.compile(r'<tr>.*?rating: (\d+).*?id="title\d+">(?:<span class="hot">Hot</span>)?(.*?)</a>.*?topicInfo">\s+((?:New)|(?:\d+ days))\s+<br',re.DOTALL)
    forum_base_urls = {'HD':'http://www.fatwallet.com/forums/hot-deals/', 'FI':'http://www.fatwallet.com/forums/finance/', \
                       'CS':'http://www.fatwallet.com/forums/contests-and-sweepstakes/','FS':'http://www.fatwallet.com/forums/free-stuff/',\
                       'TR':'http://www.fatwallet.com/forums/travel-discussion/'}
    urls_to_load = {}
    content_to_load = {}
    
    for key in forum_base_urls.keys():
        urls_to_load[key] = list()
        urls_to_load[key].append(forum_base_urls[key])
        for i in range(num_pages):
            if i == 0:
                continue
            else:
                urls_to_load[key].append(forum_base_urls[key] + '?start=' + str(  18+  (20*(i-1))  ))

    for key in urls_to_load.keys():
        if key not in content_to_load:
            content_to_load[key] = list()
        for url in urls_to_load[key]:
            try:
                f = urllib.urlopen(url) 
                content_to_load[key].append(str(f.read()))
                f.close()
            except IOError:
                sys.stderr.write("Couldn't connect to %s " % url)
                sys.exit(1)
    FWobjects_vars = {}
    FWobjects = {}
    for key in content_to_load:
        for content_item in content_to_load[key]:
            if key not in FWobjects_vars:
                FWobjects_vars[key] = list()
            FWobjects_vars[key].extend(map(list,all_pat.findall(content_item)))
            
    for key in FWobjects_vars:
        for object_list in FWobjects_vars[key]:

            object_list[0] = int(object_list[0])
            if object_list[2] == 'New':
                object_list[2] = 0
            else:
                object_list[2] = int(re.match(r'\d+',object_list[2]).group(0))
    
    for key in FWobjects_vars:
        new_list_object = []
        for list_object in FWobjects_vars[key]:
            if list_object[2] <= age_cutoff and list_object[0] > rating_cutoff:
                new_list_object.append(list_object)
        FWobjects_vars[key] = new_list_object
    email_out = ''
    for key in FWobjects_vars:
        email_out = email_out + '\n\n**************\n'
        email_out = email_out + '*****' + key + '*****\n'
        email_out = email_out + '**************\n'
        email_out = email_out + '[RATING, DESCRIPTION, AGE]\n'
        for row in sort_table(FWobjects_vars[key], (2,0)):
            email_out = email_out + str(row) + '\n'
    SendGmail(email_out)
    return

if __name__ == '__main__':
    FWFind()
