import sys
import os
import shutil
import re

from time import gmtime, strftime

 
        

vmHeader  = '#* @vtlvariable name="content" type="org.apache.turbine.services.pull.tools.ContentTool" *#\n' 
vmHeader += '#* @vtlvariable name="displayManager" type="org.nrg.xdat.display.DisplayManager" *#\n' 
vmHeader += '#* @vtlvariable name="om" type="org.nrg.xdat.om.XnatMrsessiondata" *#\n'



autoHeader =  "<!-- THIS FILE WAS AUTOGENERATED BY ($XNATImageViewer)/utility-scripts/"
autoHeader += "%s at %s -->"%(os.path.basename(__file__), strftime("%Y-%m-%d %H:%M:%S", gmtime()))
autoHeaders = ['\n']*3 + [autoHeader] + ['\n']*3




def writeTarget(target, lines):
    """
    """
    f = open(target,'w')
    for line in lines:
        f.write("%s\n" % line)
    f.close()




def makeBackup(target):
    """
    """
    shutil.move(target, os.path.join(os.path.dirname(target), os.path.basename(target).split('.')[0] + '.BKP'))




def getFileLines(path):
    """
    """
    with open(path) as f:
        content = f.readlines()
    return content




def convertDemoToPopup(demoPath):
    """ Converts the Demo.html file to the associated popup.html
    """
    #-----------------
    # Define parameters
    #-----------------
    newlines = []
    content = getFileLines(demoPath)


    for line in content:

        #
        # Replace the appropriate paths
        #
        line = line.replace('src/main/scripts/viewer/', '').strip()

        #
        # Set the Image viewer mode
        #
        if ' = ' in line and 'XNAT_IMAGE_VIEWER_MODE' in line and line.count('=') == 1:
            line = "XNAT_IMAGE_VIEWER_MODE = 'popup';";
        
        newlines.append(line)

    return newlines





def convertDemoToVM(demoPath):
    """ Converts the Demo.html file to the associated XImgView.vm
    """

    #-----------------
    # Define parameters
    #-----------------
    clearables = ['html>', 'head>', 'body>', 'title>', 'DEMO_DATA']    
    pathVal = 'projects/$om.getProject()/subjects/$om.getSubjectId()/experiments/$om.getId()'
    newlines = []
    content = getFileLines(demoPath)



    #-----------------
    # Loop through lines
    #-----------------   
    for line in content:
        #
        # Remove html tags 
        # (this works for both prepend tags and suffix tags)
        #
        for clearable in clearables:
            if clearable in line:
                line = ''

        #
        # Set the Image viewer mode
        #
        if '=' in line and 'XNAT_IMAGE_VIEWER_MODE' in line and line.count('=') == 1:
            if not 'XNAT_DATA_PATH' in line:
                line = "XNAT_IMAGE_VIEWER_MODE = 'live';";

            
        #
        # Convert filepaths to VM gets
        #
        vmChangers = ['href=', 'src=']
        for changer in vmChangers:
            if changer in line:
                lineSplit = line.split(" ")
                for word in lineSplit:
                    if changer in word:
                        word = word.replace("'", '"')
                        quoteLocations = [m.start() for m in re.finditer('"', word)]
                        
                        prefix = word[:quoteLocations[0]]
                        mid = '"$content.getURI("' + word[quoteLocations[0]+1:quoteLocations[1]] + '")"'
                        suffix = word[quoteLocations[1]+1:]
                        newWord = prefix + mid + suffix

                        line = line.replace(word, newWord)
                        

            
        #
        # Convert filepaths to appropriate directories
        #
        if 'src/main/' in line:
            line = line.replace('src/main/', '')

            
        newlines.append(line.strip())

    return [vmHeader] + newlines[1:]


    


#
# MAIN FUNCTION
#
        
def main():

    #----------------------------
    #  Params
    #----------------------------  
    imageViewerHome = os.environ.get('XNATIMAGEVIEWER_HOME')
    apacheHome = os.environ.get('CATALINA_HOME')
    demoPath =  imageViewerHome + '/Demo.html'
    vmTargets = [
        apacheHome + '/webapps/xnat/templates/screens/XImgView.vm', 
        imageViewerHome + '/src/main/templates/screens/XImgView.vm', 
    ] 
    popupTargets = [
        imageViewerHome +   '/src/main/scripts/viewer/popup.html'
    ]



    #----------------------------
    #  Get the new files as lines
    #----------------------------    
    vmLines = autoHeaders + convertDemoToVM(demoPath)
    popupLines = autoHeaders + convertDemoToPopup(demoPath)



    def makeAndWrite(lines, targets):
        for target in targets:
            makeBackup(target)
            writeTarget(target, lines)            
        


    #----------------------------
    #  Make VM
    #----------------------------
    makeAndWrite(vmLines, vmTargets)
    makeAndWrite(popupLines, popupTargets)

             
           

if __name__ == "__main__":
    main()

