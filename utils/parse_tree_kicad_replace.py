# NOTE: you need to install parsimonious, a Python library, for this to work.
# You can use pip or your favourite installer, or go here:
# https://github.com/erikrose/parsimonious
# and download and run python setup.py install from the parsimonious-master folder
#
# To generate the example_replaced.kicad_pcb file in this directory, run
# python parse_tree_kicad_replace.py example_old.kicad_pcb MyModules:SM0603-R-JRL example_new.module > example_replaced.kicad_pcb


from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import sys

# OMG KICAD file format allows parens inside quotes, ay ya, hence the more complicated "text" expressions
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
    # NOTE: you can't actually really edit parse trees, at least not easily, because
    # they all refer to the one string of text that was parsed
    # So instead, for what I'm doing, I make changes at the base most level (the individual elements, like
    # "text" above. And then to print out the tree, I spit out the base level elements, which I've edited
    # in my replace functions below
    
    def visit_text(self, n, vc):
      sys.stdout.write(n.text)
      
    def visit_opt_ws(self, n, vc):
      sys.stdout.write(n.text)
    
    def visit_ws(self, n, vc):
      sys.stdout.write(n.text)
   
    def visit_id(self, n, vc):
      sys.stdout.write(n.text)
   
    def visit_left_paren(self, n, vc):
      sys.stdout.write(n.text)
    
    def visit_right_paren(self, n, vc):
      sys.stdout.write(n.text)
         
    def generic_visit(self, n, vc):
      # with all other element visits (eg entry, item) we do nothing
      pass
        

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

# right now this code does module replace, and assumes you want to preserve the 
# fp_text elements of the old modules, as well as the position and nets of the pads. 
# It won't work if you're adding pads, or the pad ordering has changed. And it will barf
# and fail in those situations
# Outputs to standard out  

old_file = sys.argv[1]
old_module_name = sys.argv[2]
new_module_file = sys.argv[3]

f = open(old_file, 'r')
pcb = f.read()
f.close()
pcb = getModule(pcb)
f = open(new_module_file, 'r')
new_module_text = f.read()
f.close()
modules_to_update = getAllEntries(pcb, "module", old_module_name)
replacement_map = {}
for old in modules_to_update:
  # get the new module and delete the fp_texts in it
  new_module = getModule(new_module_text)
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
