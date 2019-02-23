#!/usr/bin/env python
# playing_card.py Release 7
# Created by Tin Tran 
# Comments directed to http://gimplearn.net
#
# License: GPLv3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# To view a copy of the GNU General Public License
# visit: http://www.gnu.org/licenses/gpl.html
#
#
# ------------
#| Change Log |
# ------------
# Rel 1: Initial release.
# Rel 2: JOKER card added.
# Rel 3: 2.8 and 2.10 Compatible
# Rel 4: Added Finalize toggle which merges, resizes and drop shadow
# Rel 5: Allow for custom card text
# Rel 6: Allow diagonal symmetry blend
# Rel 7: Call new gradient function instead of buggy deprecated method.
import math
import string
#import Image
from gimpfu import *
import re, tempfile
import os
#define unicodes for suites
heart = u"\u2665"
diamond = u"\u2666"
club = u"\u2663"
spade = u"\u2660"
card_values = ["A","2","3","4","5","6","7","8","9","10","J","Q","K", "JOKER","CUSTOM"]
suits = [heart,diamond,club,spade]
#from array import array
#get tempfile name here so that it only does it once instead of multiple times which clogs up document history.
#tempf=tempfile.NamedTemporaryFile(mode='w', suffix='.svg', dir=gimp.directory, delete=False)
tempf=tempfile.NamedTemporaryFile(mode='w', suffix='.svg', dir=gimp.directory, delete=False)
tempf.write("whatever")
tempf.close()
def color_to_hex(color):
	whole_color = (color[0],color[1],color[2]);
	return '#%02x%02x%02x' % whole_color
def vector_to_line_stroke(image, vector, layer, color="#000000", width=1, capstyle="butt", joinstyle="miter", miterlimit=10, shaperendering="auto",first=1):
	newelements = {
			'stroke': color,
			'stroke-width': width,
			'stroke-linecap': capstyle,
			'stroke-linejoin': joinstyle,
			'stroke-miterlimit': miterlimit,
			'shape-rendering': shaperendering,
			}
	svg = pdb.gimp_vectors_export_to_string(image, vector)
    #fix width and height to be resolution (px/inch)-independent
	svg = re.sub(r'(<svg\s[^>]*\swidth\s*=\s*)\S*"', r'\1"%dpx"' % image.width, svg, flags=re.DOTALL)
	svg = re.sub(r'(<svg\s[^>]*\sheight\s*=\s*)\S*"', r'\1"%dpx"' % image.height, svg, flags=re.DOTALL)
	svg = re.sub(r'(<path\s[^>]*)\sstroke\s*=\s*"black"', r'\1', svg, flags=re.DOTALL)
	svg = re.sub(r'(<path\s[^>]*)\sstroke-width\s*=\s*"1"', r'\1', svg, flags=re.DOTALL)
	svg = re.sub(r'(<path\s)', r'\1' + ''.join([r'%s="%s" ' % i for i in newelements.items()]), svg, flags=re.DOTALL)
	if (first == 1):
		#do nothing
		pass
	else:
		#remove xml tag, doctype tag, svg tag so that it's left with just path tag.
		svg = re.sub(r'(<\?xml\s[^>]*>)(.*)(<\!DOCTYPE\s[^>]*>)(.*)(<svg\s[^>]*>)(.*)(<path\s[^>]*>)(.*)(<\/svg>)', r'\7', svg, flags=re.DOTALL)
		#pdb.gimp_message(svg);
		
	return svg;
#custom function to append the multiple paths elements into existing svg xml.
def svg_append(svg,svgpaths):
	svg = re.sub(r'(<\?xml\s[^>]*>)(.*)(<\!DOCTYPE\s[^>]*>)(.*)(<svg\s[^>]*>)(.*)(<path\s[^>]*>)(.*)(<\/svg>)', r'\1\2\3\4\5\6\7\8', svg, flags=re.DOTALL)
	svg += svgpaths;
	svg += "</svg>";
	return svg;
#write to svg file and load as layer in GIMP
def write_to_file_and_load(image,layer,svg):
	tf = open(tempf.name,"w")
	tf.write(svg)
	tf.close()
	newlayer = pdb.gimp_file_load_layer(image, tf.name)
	#os.remove(tf.name) Try not removing it so that user can open it as svg
	image.add_layer(newlayer) #needs to be added to the image to be able to copy from
	copylayer = pdb.gimp_edit_named_copy(newlayer, "stroke")
	image.remove_layer(newlayer)
	floating_sel = pdb.gimp_edit_named_paste(layer, copylayer, True)
	pdb.gimp_floating_sel_anchor(floating_sel)
#=====================================================================================================================
def python_playing_card_tt(image, layer, card,custom, suit, fontname,blend, resize):
	pdb.gimp_image_undo_group_start(image)
	pdb.gimp_context_push()
	
	#define a 1000x1400 white image with rounded corners
	card_width = 1000
	card_height = 1400
	new_image = pdb.gimp_image_new(card_width,card_height,RGB)
	new_display = pdb.gimp_display_new(new_image)
	new_layer = pdb.gimp_layer_new(new_image,card_width,card_height,RGBA_IMAGE,"card back",100,NORMAL_MODE)
	pdb.gimp_image_insert_layer(new_image,new_layer,None,0)
	pdb.gimp_context_set_foreground((255,255,255))
	pdb.gimp_edit_fill(new_layer,FOREGROUND_FILL)
	pdb.gimp_selection_all(new_image)
	pdb.script_fu_selection_rounded_rectangle(new_image,new_layer,10,False)
	pdb.gimp_selection_invert(new_image)
	pdb.gimp_edit_clear(new_layer)
	
	#copy active layer to use as image and scale it down to 688x1116
	pdb.gimp_message("Best dimension: 688x1116")
	image_width = 688
	image_height = 1116
	image_layer = pdb.gimp_layer_new_from_drawable(layer,new_image)
	pdb.gimp_image_insert_layer(new_image,image_layer,None,0)
	pdb.gimp_layer_scale(image_layer,image_width,image_height,True)
	pdb.gimp_layer_set_offsets(image_layer,(card_width-image_width)/2.0,(card_height-image_height)/2.0)
	
	if blend == 1:
		version = pdb.gimp_version()
		
		pdb.gimp_selection_none(new_image)
		pdb.gimp_layer_resize_to_image_size(image_layer)
		image_flipped = pdb.gimp_layer_new_from_drawable(image_layer,new_image)
		pdb.gimp_image_insert_layer(new_image,image_flipped,None,0)
		pdb.gimp_item_transform_rotate_simple(image_flipped,ROTATE_180,True,0,0)
		pdb.gimp_context_set_default_colors()
		mask = pdb.gimp_layer_create_mask(image_flipped,ADD_WHITE_MASK)
		pdb.gimp_layer_add_mask(image_flipped,mask)
		if version[0:4] == "2.8.": #2.8 detected
			pdb.gimp_edit_blend(mask,FG_BG_RGB_MODE,NORMAL_MODE,GRADIENT_LINEAR,100,0,REPEAT_NONE,False, \
				False,3,0,False,card_width/2.0 + 70, card_height/2.0 - 139, \
				card_width/2.0 - 70, card_height/2.0 + 139)
		elif version[0:4] == "2.10": #2.10 detected
			pdb.gimp_context_set_gradient_blend_color_space(1)
			pdb.gimp_context_set_gradient("FG to BG (RGB)")
			pdb.gimp_context_set_gradient_fg_bg_rgb()
			pdb.gimp_context_set_gradient_repeat_mode(REPEAT_NONE)
			pdb.gimp_context_set_gradient_reverse(False)
			pdb.gimp_drawable_edit_gradient_fill(mask,GRADIENT_LINEAR,0,False,3,0,False,\
				card_width/2.0 + 70, card_height/2.0 - 139, \
				card_width/2.0 - 70, card_height/2.0 + 139)
		else:
			pdb.gimp_message("Gimp version must be 2.8 or 2.10")
		pdb.gimp_layer_remove_mask(image_flipped,MASK_APPLY)
		image_layer = pdb.gimp_image_merge_down(new_image,image_flipped,CLIP_TO_BOTTOM_LAYER)
	
	pdb.gimp_image_select_rectangle(new_image,CHANNEL_OP_REPLACE,(card_width-image_width)/2.0,(card_height-image_height)/2.0,image_width,image_height)
	pdb.script_fu_selection_rounded_rectangle(new_image,image_layer,12,False)
	pdb.plug_in_sel2path(new_image,image_layer)
	pdb.gimp_selection_invert(new_image)
	pdb.gimp_edit_clear(image_layer)
	
	line_layer = pdb.gimp_layer_new(new_image,card_width,card_height,RGBA_IMAGE,"card image outline",100,NORMAL_MODE)
	pdb.gimp_image_insert_layer(new_image,line_layer,None,0)
	pdb.gimp_selection_none(new_image)
	#stroke vectors using defined svg functions ====================
	svgpaths = "";
	stroke_width = 8
	svg = vector_to_line_stroke(new_image,new_image.vectors[0],line_layer,color_to_hex((0,0,0)),stroke_width,"square","miter",10,"auto",True)
	svg = svg_append(svg,svgpaths)
	write_to_file_and_load(new_image,line_layer,svg)
	#stroke vectors end ============================================
	if suit == 0:
		color = (255,0,0)
	elif suit == 1:
		color = (255,0,0)
	elif suit == 2:
		color = (0,0,0)
	else:
		color = (0,0,0)
	pdb.gimp_context_set_foreground(color)	
	#create values for card
	if card < 13: #regular cards
		char_width,char_height = 111,133
		text_layer = pdb.gimp_text_fontname(new_image,None,0,0,card_values[card],0,True,200,0,fontname)
		pdb.plug_in_autocrop_layer(new_image,text_layer)
		pdb.gimp_layer_scale(text_layer,char_width,char_height,True)
		pdb.gimp_layer_set_offsets(text_layer,31,66)
		# upside down value
		upside_down = pdb.gimp_layer_new_from_drawable(text_layer,new_image)
		pdb.gimp_image_insert_layer(new_image,upside_down,None,0)
		pdb.gimp_item_transform_rotate_simple(upside_down,ROTATE_180,True,0,0)
		pdb.gimp_layer_set_offsets(upside_down,card_width-31-char_width,card_height-66-char_height)
			
		#create suit for card
		char_width,char_height = 101,102
		text_layer = pdb.gimp_text_fontname(new_image,None,0,0,suits[suit],0,True,200,0,fontname)
		pdb.plug_in_autocrop_layer(new_image,text_layer)
		pdb.gimp_layer_scale(text_layer,char_width,char_height,True)
		pdb.gimp_layer_set_offsets(text_layer,37,215)
		# upside down suit
		upside_down = pdb.gimp_layer_new_from_drawable(text_layer,new_image)
		pdb.gimp_image_insert_layer(new_image,upside_down,None,0)
		pdb.gimp_item_transform_rotate_simple(upside_down,ROTATE_180,True,0,0)
		pdb.gimp_layer_set_offsets(upside_down,card_width-37-char_width,card_height-215-char_height)	
	elif card==13: #joker card
		left_x = 31
		left_y = 66
		char_width,char_height = 111,133
		for letter in "JOKER":
			text_layer = pdb.gimp_text_fontname(new_image,None,0,0,letter,0,True,200,0,fontname)
			pdb.plug_in_autocrop_layer(new_image,text_layer)
			pdb.gimp_layer_scale(text_layer,char_width,char_height,True)
			pdb.gimp_layer_set_offsets(text_layer,left_x,left_y)
			# upside down value
			upside_down = pdb.gimp_layer_new_from_drawable(text_layer,new_image)
			pdb.gimp_image_insert_layer(new_image,upside_down,None,0)
			pdb.gimp_item_transform_rotate_simple(upside_down,ROTATE_180,True,0,0)
			pdb.gimp_layer_set_offsets(upside_down,card_width-left_x-char_width,card_height-left_y-char_height)
			left_y += char_height + 16 #vertical spacing for JOKER
	elif card==14: #custom card
		left_x = 31
		left_y = 66
		char_width,char_height = 111,133
		for letter in custom:
			text_layer = pdb.gimp_text_fontname(new_image,None,0,0,letter,0,True,200,0,fontname)
			pdb.plug_in_autocrop_layer(new_image,text_layer)
			char_thickness = min(char_width,float(char_height)/text_layer.height * text_layer.width)
			pdb.gimp_layer_scale(text_layer,char_thickness,char_height,True)
			pdb.gimp_layer_set_offsets(text_layer,left_x+(char_width-char_thickness)/2.0,left_y)
			# upside down value
			upside_down = pdb.gimp_layer_new_from_drawable(text_layer,new_image)
			pdb.gimp_image_insert_layer(new_image,upside_down,None,0)
			pdb.gimp_item_transform_rotate_simple(upside_down,ROTATE_180,True,0,0)
			pdb.gimp_layer_set_offsets(upside_down,card_width-left_x-char_width+(char_width-char_thickness)/2.0,card_height-left_y-char_height)
			left_y += char_height + 16 #vertical spacing for JOKER
	#finalize our image by resizing
	if resize==1:
		result_layer = pdb.gimp_image_merge_visible_layers(new_image,EXPAND_AS_NECESSARY)
		pdb.gimp_image_scale(new_image,250,350)
		pdb.gimp_image_resize(new_image,350,450,50,50)
		pdb.gimp_layer_resize_to_image_size(result_layer)
		pdb.script_fu_drop_shadow(new_image,result_layer,2,2,15,(0,0,0),60,True)
	pdb.gimp_context_pop()
	pdb.gimp_image_undo_group_end(image)
	pdb.gimp_displays_flush()
    #return
register(
	"python_fu_playing_card_tt",                           
	"Creates playing card from active layer",
	"Creates playing card from active layer",
	"Tin Tran",
	"Tin Tran",
	"June 2018",
	"<Image>/Diego/Playing Card...",             #Menu path
	"RGB*, GRAY*", 
	[
	(PF_OPTION,"card",   "Card Value:", 0, card_values),
	(PF_STRING, "custom", "Custom (If CUSTOM value selected):", "GIMP"),
	(PF_OPTION,"suit",   "Card Suit:", 0, [heart+" Heart",diamond+" Diamond",club+" Club",spade+" Spade"]),
	(PF_FONT, "fontname", "Character font:", "Sans-serif"),
	(PF_TOGGLE, "blend",   "Diagonal Symmetry Blend:", 1),
	(PF_TOGGLE, "resize",   "Finalize (Merge/Resize/Drop shadow):", 1),
	],
	[],
	python_playing_card_tt)
main()
