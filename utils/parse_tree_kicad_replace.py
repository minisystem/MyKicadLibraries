from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import sys

# OMG the KICAD setup allows parens inside quotes, ay ya, hence the more complicated "text" expressions
grammar = """\
entry = opt_ws left_paren id ws item right_paren opt_ws
item = (text (entry / text)+) / text
text = ~"[^()\\"]*(\\".*\\")*[^()\\"]*"
opt_ws = ~"[\\n\\r\\s]*"
ws = ~"[\\n\\r\\s]+"
id = ~"[A-Z0-9_]+"i
left_paren = "("
right_paren = ")"
"""

class EntryParser(NodeVisitor):
    #def __init__(self, grammar, text):
        #self.final_entry = self.visit(ast)
    
    #def visit_entry(self, n, vc):
      #if vc[2] == "fp_line":
      #  print vc
      #return n.text
    
    #def visit_entry(self, n, vc):
    #  print vc
    
    def visit_id(self, n, vc):
      sys.stdout.write(n.text)
    
    def visit_text(self, n, vc):
      sys.stdout.write(n.text)
      
    def visit_opt_ws(self, n, vc):
      sys.stdout.write(n.text)
    
    def visit_ws(self, n, vc):
      sys.stdout.write(n.text)
   
    def visit_left_paren(self, n, vc):
      sys.stdout.write(n.text)
    
    def visit_right_paren(self, n, vc):
      sys.stdout.write(n.text)
    
    
      
    def generic_visit(self, n, vc):
      pass
        

#text_one_line = "(module SM0603-R-YAGEO (layer Bob))"
text_one_line = "(module SM0603-R-YAGEO (layer F.Cu) (tedit 5AA54555))"
text_multi_line = """
(module SM0603-R-YAGEO (layer F.Cu) (tedit 5AA54555)
  (attr smd)
  (fp_text value Val** (at 0 0) (layer F.SilkS) hide
    (effects (font (size 0.508 0.4572) (thickness 0.1143)))
  )
  )
"""

text_old = """\
(module SM0603-R-BAGEO (layer F.Cu) (tedit 5AA54555)
  (attr smd)
  (fp_text reference OmarOmar (at 0 -1.4) (layer Bobby)
    (effects (font (size 1.1111 1.1111) (thickness 1.1111)))
  )
  (fp_text value Val** (at 0 0) (layer Bobby) hide
    (effects (font (size 2.222 2.2222) (thickness 2.2222)))
  )
  (fp_line (start -1.5 -0.7) (end -0.5 -0.7) (layer Bobby) (width 0.2))
  (fp_line (start 1.5 0.7) (end 1.5 -0.7) (layer Bobby) (width 0.2))
  (fp_line (start -1.5 -0.7) (end -1.5 0.7) (layer Bobby) (width 0.2))
  (fp_line (start -1.5 0.7) (end -0.5 0.7) (layer Bobby) (width 0.2))
  (fp_line (start 0.5 -0.7) (end 1.5 -0.7) (layer Bobby) (width 0.2))
  (fp_line (start 0.5 0.7) (end 1.5 0.7) (layer Bobby) (width 0.2))
  (pad 1 smd rect (at -0.8125 0) (size 0.8125 0.8125) (layers F.Cu F.Paste F.Mask))
  (pad 2 smd rect (at 0.8125 0) (size 0.8125 0.8125) (layers F.Cu F.Paste F.Mask))
  (model Resistors_SMD.3dshapes/R_0603.wrl
    (at (xyz 0 0 0.001))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )
)
"""

text_new = """\
(module MyModules:SM0603-R-YAGEO (layer F.Cu) (tedit 5AA54555)
  (attr smd)
  (fp_text reference SM0603 (at 0 -1.4) (layer F.SilkS)
    (effects (font (size 0.6096 0.6096) (thickness 0.1524)))
  )
  (fp_text value Val** (at 0 0) (layer F.SilkS) hide
    (effects (font (size 0.508 0.4572) (thickness 0.1143)))
  )
  (fp_line (start -1.5 -0.7) (end -0.5 -0.7) (layer F.SilkS) (width 0.2))
  (fp_line (start 1.5 0.7) (end 1.5 -0.7) (layer F.SilkS) (width 0.2))
  (fp_line (start -1.5 -0.7) (end -1.5 0.7) (layer F.SilkS) (width 0.2))
  (fp_line (start -1.5 0.7) (end -0.5 0.7) (layer F.SilkS) (width 0.2))
  (fp_line (start 0.5 -0.7) (end 1.5 -0.7) (layer F.SilkS) (width 0.2))
  (fp_line (start 0.5 0.7) (end 1.5 0.7) (layer F.SilkS) (width 0.2))
  (pad 1 smd rect (at -0.8125 0) (size 0.8125 0.8125) (layers F.Cu F.Paste F.Mask))
  (pad 2 smd rect (at 0.8125 0) (size 0.8125 0.8125) (layers F.Cu F.Paste F.Mask))
  (model Resistors_SMD.3dshapes/R_0603.wrl
    (at (xyz 0 0 0.001))
    (scale (xyz 1 1 1))
    (rotate (xyz 0 0 0))
  )
)
"""

def removeChildrenAndWalk(node, to_remove):
    bad = []
    for c in node.children:
      if c.expr_name == "entry" and c.children[2].text == to_remove:
        bad.append(c)
    
    for b in bad:
      node.children.remove(b)
    
    for c in node.children:
      removeChildrenAndWalk(c, to_remove)

def replaceElementText(node, parent_name, parent_match, node_match, new_text):
  #if node.expr_name == "entry":
  #  print "--", parent_name
  #  for c in node.children:
  #    print c.expr_name,
  #  print node.children[2].text, len(node.children[2].text)
  
  if parent_name == parent_match:
    #print parent_name
    if node.expr_name == "entry" and node.children[2].text == node_match:
      # this deep dive into the children[2] element is because it's an ITEM, and
      # we need to get down to its basic type, which is text, which is inside another NODE,
      # deep deep deep.. 
      n = node.children[4].children[0].children[0]
      # print n.text
      n.full_text = new_text
      n.start = 0
      n.end = len(new_text)
      
  if node.expr_name == "entry":
    parent_name = node.children[2].text
    # print parent_name
  
  
  for c in node.children:
    replaceElementText(c, parent_name, parent_match, node_match, new_text)


def getModule(module_text):
  ast = Grammar(grammar).parse(module_text)
  return ast
  
def getAllEntries(node, entry_id, entry_name=""):
  match = []
  if node.expr_name == "entry" and node.children[2].text == entry_id:
    if entry_name in node.text:
      match = [node]
  for c in node.children:
    match = match + getAllEntries(c, entry_id, entry_name)
  return match

def addAfter(node, node_name, new_nodes):
  if node.expr_name == "entry" and node.children[2].text == node_name:
    return True
  for c in node.children:
    if addAfter(c, node_name, new_nodes):
      node.children = node.children + new_nodes
  return False

def replaceNodes(node, rep_map):
  for c in node.children:
    if c in rep_map:
      node.children[node.children.index(c)] = rep_map[c]
    else:
      replaceNodes(c, rep_map)
  

f = open('C:\\Users\\Omar\\Downloads\\750 LFO S&H NOISE SLEW.kicad_pcb', 'r')
pcb = f.read()
pcb = getModule(pcb)
modules_to_update = getAllEntries(pcb, "module", "MyModules:SM0603-R-JRL")
replacement_map = {}
for old in modules_to_update:
  # get the new module and delete the fp_texts in it
  new_module = getModule(text_new)
  removeChildrenAndWalk(new_module, "fp_text")
  
  # add in all the key elements from the old module
  at = getAllEntries(old, "at")[0]
  path = getAllEntries(old, "path")[0]
  texts = getAllEntries(old, "fp_text")
  addAfter(new_module, "tedit", [at, path] + texts)
  
  # get the layer in the old module for module
  layer = getAllEntries(old, "layer")[0]
  layer_name = layer.children[4].text
  replaceElementText(new_module, "module", "module", "layer", layer_name)
  
  # get the layer in the old module for fp_line
  fp_line = getAllEntries(old, "fp_line")[0]
  layer = getAllEntries(fp_line, "layer")
  layer_name = layer[0].children[4].text
  replaceElementText(new_module, "", "fp_line", "layer", layer_name)
  
  # get the layers in the pads and fix those up
  pad = getAllEntries(old, "pad")[0]
  layers = getAllEntries(pad, "layers")
  layers_name = layers[0].children[4].text
  replaceElementText(new_module, "", "pad", "layers", layers_name)
  replacement_map[old] = new_module
  
  # get the old pads nets, and add them to the new pads
  old_pads = getAllEntries(old, "pad")
  new_pads = getAllEntries(new_module, "pad")
  assert len(old_pads) == len(new_pads)
  for op, np in zip(old_pads, new_pads):
    assert op.text[:5] == np.text[:5] # this makes sure that we are netting pad 1 to pad 1, etc.. 
    net = getAllEntries(op, "net")
    addAfter(np, "layers", net)
  
  #ep = EntryParser()
  #ep.visit(new_module)
  #break

replaceNodes(pcb, replacement_map)
ep = EntryParser()
# this outputs to stdout, so you need to direct the output to a file, like so:
# python parse_tree_kicad_replace.py > new.pcb
ep.visit(pcb)
