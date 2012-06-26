#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, zipfile, xml.dom.minidom, re, json

articlechilds=['Point 0', 'Point 0 (number)', 'Standard', 'Manual NumPar 1', 'NumPar 1', 'Manual Heading 4', 'Manual NumPar 2']
paragraphkids=['Point 1', 'Point 1 (letter)', 'Text 1']
listtypes=['Point 0', 'Point 0 (number)', 'Manual NumPar 1', 'NumPar 1', 'Manual Heading 4', 'Manual NumPar 2', 'Point 1', 'Point 1 (letter)']
numberlists=['NumPar 1']

## u"Default": "p",
## u"Fait à": "",
## u"Institution qui signe": "",
## u"Intérêt EEE": "",
## u"Personne qui signe": "",
## u"Statut": "",

class Node:
    def __init__ (self, title, tpe=None) :
        self.title=title
        self.nodes=[]
        self.type=tpe

    def __repr__ (self):
        nodes=u', '.join((repr(x) for x in self.nodes))
        if self.type:
            res= u"<%s: %s [%s]>" % (self.type, self.title, nodes)
        elif nodes:
            res= u"<%s [%s]>" % (self.title, nodes)
        else:
            res= u"<%s>" % self.title
        return res.encode('utf8')

    def add(self, node):
        # if last item is a list and this contains the same type as
        # node, then append it there
        if (self.nodes and
            self.nodes[-1].type == 'list' and
            self.nodes[-1].title == node.type):
            self.nodes[-1].nodes.append(node)
            return node
        # check if type is list, if so, create a container and append
        # that to self
        if node.type in listtypes:
            container = Node(node.type, 'list')
            container.nodes.append(node)
            node = container
        self.nodes.append(node)
        return node

    def dump(self,ind=0):
        if self.type!='list':
            if self.type in ['article', 'section']: print '\n'
            if ind>0: print ' ' * (ind * 2),
            print self.title.encode('utf8')
        [x.dump(ind+1) for x in self.nodes]

    def json(self):
        return { 'title': self.title,
                 'type': self.type,
                 'kids': [x.json() for x in self.nodes]}

    def html(self):
        res=[]
        kids=[y for x in self.nodes for y in x.html()]
        if self.type!='list':
            if self.type == 'article':
                res.append(u"<h5 class='article' id='%s'>%s</h5>" %
                           ('-'.join(self.title.lower().split(None,2)[:2]), self.title))
                if kids:
                    res.append(u"<ul class='paragraphs'>%s</ul>" % u'\n\t'.join(kids))
            elif self.type == 'section':
                res.append(u"<h4 class='section' id='%s'>%s</h4>" %
                           ('-'.join(self.title.lower().split(None,2)[:2]), self.title))
                if kids:
                    res.append(u'\n\t'.join(kids))
            elif self.type in numberlists:
                clss='-'.join(self.type.lower().split())
                res.append("<li class='decimal %s'>%s\n%s</li>" % (clss,
                                                           self.title,
                                                           u'\n'.join(kids)))
            elif self.type in listtypes:
                if ' (letter)' in self.type:
                    clss='letter'
                elif ' (number)' in self.type:
                    clss='number'
                else:
                    clss='-'.join(self.type.lower().split())
                res.append("<li class='%s'>%s\n%s</li>" % (clss,
                                                           self.title,
                                                           u'\n'.join(kids)))
            else:
                res.append("<p class='%s'>%s\n%s</p>" % ('-'.join(self.type.lower().split()),
                                                         self.title,
                                                         u'\n'.join(kids)))
                return res
        else:
            if ' (letter)' in self.title:
                res.extend(["<ol class='letter %s'>" % '-'.join(self.title.lower().split()),
                            u'\n\t'.join(kids),
                            "</ol>"])
            elif ' (number)' in self.title:
                res.extend(["<ol class='number %s'>" % '-'.join(self.title.lower().split()),
                            u'\n\t'.join(kids),
                            "</ol>"])
            else:
                res.extend(["<ul class='%s'>" % '-'.join(self.title.lower().split()),
                            u'\n\t'.join(kids),
                            "</ul>"])
        return res

class ODT:
    def __init__ (self, path) :
        self.footnotes = []
        self.preamble = []
        self.recitals = []
        self.chaps = []
        self.ref = ""
        self.type = ""
        self.title = ""
        self.institutions = ""
        self.adoption = ""
        self.load(path)

    def load(self, filepath) :
        zip = zipfile.ZipFile(filepath)
        self.content = xml.dom.minidom.parseString(zip.read("content.xml"))
        zip.close()

        styles = dict([(style.getAttribute('style:name'),
                        style.getAttribute('style:parent-style-name'))
                       for style
                       in self.content.getElementsByTagName("style:style")])
        paragraphs = self.content.getElementsByTagName("text:p")

        prev = None
        stack = {}
        for paragraph in paragraphs :
            style=styles.get(paragraph.getAttribute("text:style-name"),'') \
                   .replace('_20_',' ') \
                   .replace('_27_',"'") \
                   .replace("_28_","(") \
                   .replace("_29_",")")

            if style == u"Application directe":
                break

            elif style == u"Référence interinstitutionnelle":
                self.ref = self.textToString(paragraph)

            elif style == u"Formule d'adoption":
                self.adoption = self.textToString(paragraph)

            elif style == u"Type du document":
                self.type = self.textToString(paragraph)

            elif style == u"Titre objet":
                self.title = self.textToString(paragraph)

            elif style == u"Institution qui agit":
                self.institutions = self.textToString(paragraph)

            elif style == u"Considérant":
                self.recitals.append(self.textToString(paragraph))

            elif not stack and style == u"Standard":
                self.preamble.append(self.textToString(paragraph))

            elif style == u"ChapterTitle":
                if style == prev:
                    last = stack['chapter']
                    last.title="%s %s" % (last.title, self.textToString(paragraph))
                    #print 'append', last.title
                else:
                    node = Node(self.textToString(paragraph),'chapter')
                    self.chaps.append(node)
                    stack = { 'chapter': node }
                    #print 'new',stack['chapter'].title

            elif style == u"SectionTitle":
                if style == prev:
                    last = stack['section']
                    last.title="%s %s" % (last.title, self.textToString(paragraph))
                else:
                    node = Node(self.textToString(paragraph),'section')
                    stack['chapter'].nodes.append(node)
                    stack = { 'chapter': stack['chapter'],
                              'section': node }

            elif style == u"Titre article":
                if style == prev:
                    last = stack['article']
                    last.title="%s %s" % (last.title, self.textToString(paragraph))
                else:
                    target = 'section' if 'section' in stack else 'chapter'
                    node = Node(self.textToString(paragraph),'article')
                    stack[target].add(node)
                    stack = dict([x for x in stack.items() if x[0] in ['chapter', 'section']])
                    stack['article']=node

            elif stack:
                #print style.encode('utf8')
                if style in articlechilds:
                    tmp=Node(self.textToString(paragraph), style)
                    stack['article'].nodes.append((tmp))
                    stack['list'] = tmp
                elif style in paragraphkids:
                    stack['list'].add(Node(self.textToString(paragraph), style))
                else:
                    print >>sys.stderr, '[!] unknown style', style

            else:
                print >>sys.stderr, "<%s>%s</%s>" % (style.encode('utf8'),
                                                     self.textToString(paragraph).encode('utf8'),
                                                     style.encode('utf8'))
            prev = style

    def dump(self):
        print self.ref, self.title
        print
        for p in self.preamble:
            print p
        print
        for i, r in enumerate(self.recitals):
            print (u"  (%s) %s" % (i+1,r)).encode('utf8')
            print
        print
        print self.adoption
        print
        for c in self.chaps:
            print
            print c.title
            for x in c.nodes: x.dump()
        print
        print "Footnotes"
        for i, r in enumerate(self.footnotes):
            print (u"  (%s) %s" % (i+1,r)).encode('utf8')

    def json(self):
        return [{ 'title': c.title,
                  'kids': [x.json() for x in c.nodes]}
                for c in self.chaps]

    def html(self):
        res=[css]
        res.append("<h2><span id='reference'>%s</span> <span id='title'>%s</span></h2>" %
                   (self.ref, self.title))

        res.extend(["<p class='preamble'>%s</p>" % p
                    for p in self.preamble])

        tmp=[u"<li class='recital' id='recital_%s'>%s</li>" % (i+1,r)
             for i, r in enumerate(self.recitals)]
        res.append("<ol class='number '>%s</ol>" % '\n'.join(tmp))

        res.append("<p class='adoption'>%s</p>" % self.adoption)

        for i, c in enumerate(self.chaps):
            res.append("<h3 class='chapter' id='chapter%s'>%s</h3>" %
                       (i+1, c.title))
            res.append("<ol>")
            for x in c.nodes:
                res.extend(x.html())
            res.append("</ol>")

        res.append("<hr /><h3>Footnotes</h3>")
        res.extend([u"<p class='footnote'><a name='footnote%s'>[%s] %s</a></p>" % (i+1, i+1 ,r[1])
                    for i, r in enumerate(self.footnotes)])

        return u'\n'.join(res).encode('utf8')

    def textToString(self, element):
        buffer = u""
        for node in element.childNodes :
            if node.nodeType == xml.dom.Node.TEXT_NODE :
                buffer += node.nodeValue

            elif node.nodeType == xml.dom.Node.ELEMENT_NODE :
                tag = node.tagName

                if tag == "text:span" :
                    text = self.textToString(node)
                    if not text.strip() :
                        return ""  # don't apply styles to white space
                    buffer += text

                elif tag == "text:note" :
                    cite = (node.getElementsByTagName("text:note-citation")[0]
                                .childNodes[0].nodeValue)
                    body = (node.getElementsByTagName("text:note-body")[0]
                                .childNodes[0])
                    self.footnotes.append((cite, self.textToString(body)))
                    buffer += "[^%s]" % cite

                elif tag == "text:s" :
                    try :
                        num = int(node.getAttribute("text:c"))
                        buffer += " "*num
                    except :
                        buffer += " "

                elif tag == "text:tab" :
                    buffer += "    "

                elif tag == "text:a" :
                    text = self.textToString(node)
                    link = node.getAttribute("xlink:href")
                    buffer += "[%s](%s)" % (text, link)
                else: buffer += " "
        return u' '.join(buffer.split())

css="""
<style>
li { list-style: none outside none; margin: .8em; }
ol {
  counter-reset: list;
}
ol li {
  list-style: none;
}
ol li.number:before,
ol li.recital:before {
  content: "(" counter(list, decimal) ") ";
  counter-increment: list;
}
ol li.decimal:before {
  content: counter(list, decimal) ". ";
  counter-increment: list;
}
ol li.letter:before {
  content: "(" counter(list, lower-latin) ") ";
  counter-increment: list;
}
</style>
"""
if __name__ == "__main__" :
    odt = ODT(sys.argv[1])
    #odt.dump()
    #for x in odt.chaps:
    #    print >>sys.stderr, x
    print odt.html()
    #print json.dumps(odt.json(), indent=1, ensure_ascii=False).encode('utf8')
