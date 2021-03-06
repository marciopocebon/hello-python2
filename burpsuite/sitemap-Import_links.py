from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL
from javax import swing
# from javax.swing import JOptionPane
from javax.swing.filechooser import FileNameExtensionFilter
import threading
import os


class BurpExtender(IBurpExtender, IContextMenuFactory):
    """Import urls into sitemap from a file.
    """
    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.context = None

        callbacks.setExtensionName("Sitemap Importer")
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Import Links from a file", actionPerformed=self.custom_menu))

        return menu_list

    def custom_menu(self, event):
        self.sitemap_importer_from_file()
        return

    def custom_dialog(self):
        filename = None
        fChooser = swing.JFileChooser()
        extfilter = swing.filechooser.FileNameExtensionFilter("OK", ["*"])
        fChooser.addChoosableFileFilter(extfilter)
        files = fChooser.showDialog(None, "URLs files")

        if files == swing.JFileChooser.APPROVE_OPTION:
            filename = fChooser.getSelectedFile().getPath()

        return filename

    def sitemap_importer_from_file(self):
        filename = self.custom_dialog()
        # filename = JOptionPane.showInputDialog("Import Links from a file")

        if filename and os.path.exists(filename):
            for url in open(filename):  # Not to large.
                url = url.strip()
                t = threading.Thread(target=self.sitemap_importer, args=[url])
                t.daemon = True
                t.start()
            self.callbacks.printOutput('[*] All urls imported.')
        else:
            self.callbacks.printOutput('[*] Please select a urls file.')

    def sitemap_importer(self, http_url):
        java_URL = URL(http_url)

        port = 443 if java_URL.protocol == 'https' else 80
        port = java_URL.port if java_URL.port != -1 else port
        httpService = self.helpers.buildHttpService(java_URL.host, port, java_URL.protocol)
        httpRequest = self.helpers.buildHttpRequest(URL(http_url))

        self.callbacks.addToSiteMap(self.callbacks.makeHttpRequest(httpService, httpRequest))


# Platform:           Mac OS X / Windows 7
# Brupsuite Version:  1.7.11
# Author:             Nixawk
# https://portswigger.net/burp/help/extender.html
# https://portswigger.net/burp/extender/api/index.html
# https://portswigger.net/burp/extender/api/burp/IHttpService.html
# https://support.portswigger.net/customer/en/portal/topics/719885-burp-extensions/questions?page=8
# http://docs.oracle.com/javase/7/docs/api/java/net/URL.html#URL(java.lang.String)
# http://stackoverflow.com/questions/12810460/joptionpane-input-dialog-box-program
