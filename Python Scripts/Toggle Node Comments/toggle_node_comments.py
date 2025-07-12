def toggle_all_node_comments():
    #Gets every node in the file
    all_nodes = hou.node('/').allSubChildren()
    
    #Checks whether the comment is currently visible or not
    current_state = all_nodes[0].isGenericFlagSet(hou.nodeFlag.DisplayComment)

    #Loops through every node in the file and turns the comments on or off
    for node in all_nodes:
        node.setGenericFlag(hou.nodeFlag.DisplayComment, not current_state)

#Calls the function to run the code
toggle_all_node_comments()