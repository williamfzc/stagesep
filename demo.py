import stagesep


# design
# still not implemented

# begin
stagesep_object = stagesep.load_video()

# operation
stagesep_object = stagesep_object.rebuild_video()

# get result
stage_list = stagesep_object.get_stage()
