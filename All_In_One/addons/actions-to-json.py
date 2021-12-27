# The goal of this addon is to export all of the actions for the active
# armature into a JSON file

bl_info = {
    "name": "Export Actions to JSON",
    "category": "Learnbgame",
}

import bpy
import math
import sys

class ExportActionsToJSON(bpy.types.Operator):
    """Given an active armature, export it's actions and keyframed bone pose information to a JSON file"""
    # Unique identifier for the addon
    bl_idname = 'import_export.actions2json'
    # Display name in the interface
    bl_label = 'Export Actions to JSON'
    bl_options = {'REGISTER'}
    bl_category = 'Import-Export'
    # If a filepath argument is passed into the addon we use it instead of reading a filepath from the CLI
    filepath = bpy.props.StringProperty(name='filepath')

    def execute(self, context):
        # Get all of the keyframes for the current action
        def getActionKeyframes(action):
            keyframes = []
            for fcurve in action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    x, y = keyframe.co
                    # Don't know why yet, but we encounter each keyframes a
                    # bunch of times. so need to make sure we only add them once
                    if x not in keyframes:
                        # convert from float to int and insert into our keyframe list
                        keyframes.append((math.ceil(x)))
            return keyframes

        # Get all of the bone pose matrices for the current keyframe
        # So if there are 10 bones, we'll get 10 matrices representing
        # these bones' orientations at this point in time
        def getBonePosesAtKeyframe(frame, armature, boneNames):
            stringifiedBones = ''
            bpy.context.scene.frame_set(frame)
            for boneName in boneNames:
                poseBone = armature.pose.bones[boneName]
                stringifiedMatrix = stringifyMatrix(poseBone.matrix)
                # Trailing comma until you get to the last bone
                stringifiedBones += '      ' + stringifiedMatrix
                # Add a comma to the end of every bone
                # in the array excluding the last one
                if boneName != boneNames[-1]:
                    stringifiedBones += ','
                stringifiedBones += '\n'
            return stringifiedBones

        # Convert a matrix into string
        #   i.e. '[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1 ]'
        # Right now we round elements in the matrix to 6 decimal places.
        # I just picked a number. We can explore trade-offs
        def stringifyMatrix (matrix):
            stringifiedMatrix = '['
            for column in range(0, 4):
                for row in range(0, 4):
                    if (column == 3 and row == 3):
                        # TODO: Accept a precision flag to grant control over the rounding of matrix values?
                        stringifiedMatrix += str(matrix[column][row])
                    else:
                        # TODO: Accept a precision flag to grant control over the rounding of matrix values?
                        stringifiedMatrix += str(matrix[column][row]) + ', '
            stringifiedMatrix += ']'
            return stringifiedMatrix

        # Get the armature that is currently active. We will be parsing it's actions
        # TODO: Error message if the active object is not the armature
        activeArmature = bpy.context.scene.objects.active
        # If the active object isn't an armature, we use the first armature that we find
        if activeArmature.type != 'ARMATURE':
            for obj in bpy.context.scene.objects:
                if obj.type == 'ARMATURE':
                    activeArmature = obj
                    bpy.context.scene.objects.active = activeArmature
                    break

        # Get all of the actions
        # TODO: If we later support handling multiple armatures we'll need to only use the
        # actions that apply to the current armature
        actionsList = list(bpy.data.actions)
        bpy.ops.object.mode_set(mode = 'POSE')

        # Select all of the armature's bones so that we can iterate over them later
        # We get all bone names so that we are certain to always iterate over bones in a consistent
        # order. We've had issues in the past where the order would be different depending on how you
        # accessed the bones, so this should help prevent future errors.
        allBoneNames = []
        for poseBone in activeArmature.pose.bones:
            poseBone.bone.select = True
            allBoneNames.append(poseBone.name)
        # Start building our JSON
        # The format is
        # {
        #   someAction: { timeInSeconds: [bone1, bone2, bone3 ...], keyframe2: [bone1, bone2, bone3 ...] },
        #   anotherAction: { someTime: [bone1, bone2, bone3 ...], keyframe2: [bone1, bone2, bone3 ...], anotherTime: { ... } },
        # }
        jsonActionData = '{\n  "actions": {\n'
        for actionInfo in actionsList:
            # Change to the action that we are currently parsing the data of
            activeArmature.animation_data.action = bpy.data.actions.get(actionInfo.name)
            # Get all of the keyframes for the current action. We'll iterate through them
            # to get all of the bone data
            actionKeyframes = getActionKeyframes(activeArmature.animation_data.action)
            # If this action has no keyframes we skip it
            if actionKeyframes == []:
                 continue
            # someAction: {
            jsonActionData += '  "' + actionInfo.name + '": { \n'
            # Loop through the keyframes and build the frame data for the action
            # We convert keyframes into times in seconds
            for frame in actionKeyframes:
                # Round the keyframes time in seconds to 6 decimal places.
                # i.e. 10.333333 seconds
                timeOfKeyframe = round(frame / bpy.context.scene.render.fps, 6)
                # So here, at 24FPS, frame 12 would become `0.5` (seconds)
                jsonActionData += '    "' + str(timeOfKeyframe) + '": [\n'
                # Get all of the bone pose matrices for this frame -> [bone1Matrix, bone2Matrix, ..]
                jsonActionData += getBonePosesAtKeyframe(frame, activeArmature, allBoneNames)
                jsonActionData += '    ],\n'
            # Get rid of the last trailing comma for the keyframe times
            jsonActionData = jsonActionData.rstrip('\r\n').rstrip(',') + '\n'
            jsonActionData += '  },\n'

        # Get rid of the last trailing comma for the action names
        jsonActionData = jsonActionData.rstrip('\r\n').rstrip(',')
        jsonActionData += '  },\n"inverseBindPoses": [\n'

        # Now that we've added our actions we add our bind poses
        # We iterate over pose bones instead of edit bones to ensure a consistent ordering
        # of bone data
        for boneName in allBoneNames:
            # Calculate the bone's inverse bind matrix
            #
            # taken from:
            #   https://blenderartists.org/forum/showthread.php?323968-Exporting-armature-amp-actions-how-do-you-get-the-bind-pose-and-relative-transform
            #   https://blender.stackexchange.com/a/15229/40607
            #
            # TODO: Not currently handling the case where a bone has a parent since I'm using blender-iks-to-fks
            # which clears all parent relationships before visual keying
            poseBone = activeArmature.pose.bones[boneName]

            # We make sure to account for the world offset of the armature since matrix_local is in armature space
            boneBindMatrix = activeArmature.matrix_world * poseBone.bone.matrix_local
            boneInverseBind = boneBindMatrix.copy().inverted()

            stringifiedBindPose = stringifyMatrix(boneInverseBind)
            jsonActionData += stringifiedBindPose + ',\n'

        # Get rid of the last trailing comma for the bind poses names
        jsonActionData = jsonActionData.rstrip('\r\n').rstrip(',')
        jsonActionData += '],\n'

        # Now we create the JSON for the joint name indices. The bind poses and keyframe poses are
        # arrays of index 0...numBones - 1. To look up a bone in this array you use its joint name index
        jsonActionData += '"jointNameIndices": {\n'
        for index, boneName in enumerate(allBoneNames):
            jsonActionData += '"' + boneName + '": ' + str(index) + ','

        # Get rid of the last trailing comma for the joint indices
        jsonActionData = jsonActionData.rstrip('\r\n').rstrip(',')
        jsonActionData += '}'
        jsonActionData += '\n}'
        # print(jsonActionData)
        # Write out data to a file
        # file = '/var/tmp/foo.json'
        argv = sys.argv
        # Get all args after `--`
        argv = argv[argv.index('--') + 1:]
        file = self.filepath or argv[0]
        with open(file, 'w') as outputFile:
            outputFile.write(jsonActionData)

        return {'FINISHED'}

def register():
    bpy.utils.register_class(ExportActionsToJSON)

def unregister():
    bpy.utils.unregister_class(ExportActionsToJSON)

if __name__ == "__main__":
    register()
