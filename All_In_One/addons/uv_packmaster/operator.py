
import subprocess
import queue
import threading

from .utils import *
from .connection import *

import bmesh
import bpy
import mathutils
import tempfile


class InvalidTopologyError(BaseException):
    pass

class InconsistentMaterialError(BaseException):
    def __init__(self, p_context):
        self.p_context = p_context


class UVP_OT_PackOperatorGeneric(bpy.types.Operator):

    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.mode == 'EDIT'

    def get_topo_analysis_level(self):
        prefs = get_prefs()

        if prefs.FEATURE_self_intersect_processing and prefs.allow_self_intersect:
            return UvTopoAnalysisLevel.PROCESS_SELF_INTERSECT
        elif prefs.extended_topo_analysis:
            return UvTopoAnalysisLevel.EXTENDED

        return UvTopoAnalysisLevel.DEFAULT

    def check_packer_retcode(self, retcode):
        if retcode in {UvPackerErrorCode.SUCCESS, UvPackerErrorCode.INVALID_TOPOLOGY, UvPackerErrorCode.NO_SPACE}:
            return

        if retcode == UvPackerErrorCode.NO_VALID_STATIC_ISLAND:
            raise RuntimeError("'Pack To Others' option enabled, but no unselected island found in the unit UV square")

        if retcode == UvPackerErrorCode.UNEXPECTED_INVALID_TOPOLOGY:
            raise RuntimeError("Unexpected topology error encoutered. Consider reporting the UV map to the developers")

        if retcode == UvPackerErrorCode.MAX_GROUP_COUNT_EXCEEDED:
            raise RuntimeError("Maximal group count exceeded")

        raise RuntimeError('Pack process returned an error')

    def raiseUnexpectedOutputError(self):
        raise RuntimeError('Unexpected output from the pack process')

    def exit_common(self):
        wm = self.p_context.context.window_manager
        wm.event_timer_remove(self._timer)
        self.p_context.update_meshes()

    def process_invalid_islands(self):
        if self.invalid_islands_msg is None:
            self.raiseUnexpectedOutputError()

        invalid_islands = read_int_array(self.invalid_islands_msg)

        if len(invalid_islands) > 0:
            handle_invalid_islands(self.p_context, invalid_islands)
            self.report({'ERROR'}, 'Invalid topology encountered. Check selected islands or adjust topology options')
            raise InvalidTopologyError()

    def finish(self, context):
        self.connection_thread.join()

        try:
            self.packer_proc.wait(5)
        except:
            raise RuntimeError('The packer process wait timeout reached')

        self.check_packer_retcode(self.packer_proc.returncode)

        self.process_invalid_islands()
        self.process_result()
        self.exit_common()

        return {'FINISHED'}

    def cancel(self, context):
        self.packer_proc.terminate()
        # self.progress_thread.terminate()

        self.exit_common()
        return {'FINISHED'}

    def get_progress_msg(self):
        prefs = get_prefs()

        if self.curr_phase == UvPackingPhaseCode.INITIALIZATION:
            return 'Initialization'

        if self.curr_phase == UvPackingPhaseCode.TOPOLOGY_ANALYSIS:
            return "Topology analysis: {:3}% (press ESC to cancel)".format(self.curr_progress)

        if self.curr_phase == UvPackingPhaseCode.PACKING_INITIALIZATION:
            return 'Pack initialization (press ESC to cancel)'

        if self.curr_phase == UvPackingPhaseCode.OVERLAP_CHECK:
            return 'Overlap check in progress (press ESC to cancel)'

        if self.curr_phase == UvPackingPhaseCode.AREA_MEASUREMENT:
            return 'Area measurement in progress (press ESC to cancel)'

        if self.curr_phase == UvPackingPhaseCode.SIMILAR_SELECTION:
            return 'Looking for similar islands (press ESC to cancel)'

        if self.curr_phase == UvPackingPhaseCode.RENDER_PRESENTATION:
            return 'Close the demo window to finish'

        if self.curr_phase == UvPackingPhaseCode.TOPOLOGY_VALIDATION:
            return "Topology validation: {:3}% (press ESC to cancel)".format(self.curr_progress)

        if self.curr_phase == UvPackingPhaseCode.VALIDATION:
            return "Per-face overlap check: {:3}% (press ESC to cancel)".format(self.curr_progress)

        if self.curr_phase == UvPackingPhaseCode.PACKING:
            if prefs.FEATURE_heuristic_search and prefs.heuristic_search_time > 0:
                now = time.time()
                sec_elapsed = int(now - self.packing_start_time)
                sec_left = max(0, prefs.heuristic_search_time - sec_elapsed)

                return "Search time left: {:3} sec. Iteration progress: {:3}% (press ESC to cancel)".format(sec_left,
                                                                                                            self.curr_progress)

            return "Pack progress: {:3}% (press ESC to cancel)".format(self.curr_progress)

        raise RuntimeError('Unexpected packing phase encountered')

    def handle_progress_msg(self):
        msg_refresh_interval = 2.0

        new_progress_msg = self.get_progress_msg()
        now = time.time()
        if now - self.pmsg_last_update > msg_refresh_interval or new_progress_msg != self.progress_msg:
            self.pmsg_last_update = now
            self.progress_msg = new_progress_msg
            self.report({'INFO'}, self.progress_msg)

    def handle_packer_msg(self, msg):
        msg_code = force_read_int(msg)

        if msg_code == UvPackMessageCode.PROGRESS_REPORT:
            self.curr_phase = force_read_int(msg)
            self.curr_progress = force_read_int(msg)

        elif msg_code == UvPackMessageCode.INVALID_ISLANDS:
            if self.invalid_islands_msg is not None:
                self.raiseUnexpectedOutputError()

            self.invalid_islands_msg = msg

        elif msg_code == UvPackMessageCode.ISLAND_FLAGS:
            if self.island_flags_msg is not None:
                self.raiseUnexpectedOutputError()

            self.island_flags_msg = msg

        elif msg_code == UvPackMessageCode.PACK_SOLUTION:
            if self.pack_solution_msg is not None:
                self.raiseUnexpectedOutputError()

            self.pack_solution_msg = msg

        elif msg_code == UvPackMessageCode.AREA:
            if self.area_msg is not None:
                self.raiseUnexpectedOutputError()

            self.area_msg = msg

        elif msg_code == UvPackMessageCode.INVALID_FACES:
            if self.invalid_faces_msg is not None:
                self.raiseUnexpectedOutputError()

            self.invalid_faces_msg = msg

        elif msg_code == UvPackMessageCode.SIMILAR_ISLANDS:
            if self.similar_islands_msg is not None:
                self.raiseUnexpectedOutputError()

            self.similar_islands_msg = msg

        else:
            self.raiseUnexpectedOutputError()

    def handle_communication(self):
        while True:
            try:
                item = self.progress_queue.get_nowait()
            except queue.Empty as ex:
                break

            if isinstance(item, str):
                raise RuntimeError(item)
            elif isinstance(item, io.BytesIO):
                self.handle_packer_msg(item)
            else:
                raise RuntimeError('Unexpected output from the connection thread')

    def modal(self, context, event):
        prefs = get_prefs()
        cancel = False

        try:
            if event.type == 'ESC':
                self.report({'INFO'}, 'Operation cancelled by user')
                cancel = True
            elif event.type == 'TIMER':
                self.handle_communication()

                if self.curr_phase == UvPackingPhaseCode.DONE:
                    return self.finish(context)

                # Check whether packer process is alive
                if self.packer_proc.poll() is not None:
                    raise RuntimeError('Packer process died unexpectedly')

                self.handle_progress_msg()

        except InvalidTopologyError:
            cancel = True

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, str(ex))
            cancel = True
        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'Unexpected error')
            cancel = True

        if cancel:
            return self.cancel(context)

        return {'RUNNING_MODAL'}

    def execute(self, context):
        cancel = False

        objs = context.selected_objects
        self.p_context = PackContext(context, objs)

        try:
            if not in_debug_mode():
                platform_check_op()

            prefs = get_prefs()
            send_unselected = self.send_unselected_islands()
            self.p_context.gather_uv_data(send_unselected)

            self.validate_pack_params()

            island_materials = None
            prev_mat_id = None
            nequal_count = 0

            if self.prepare_material_map():
                mat_count = self.p_context.prepare_material_map()

                if len(self.p_context.inconsistent_islands) > 0:
                    raise InconsistentMaterialError(self.p_context)

                if mat_count == 1:
                    raise RuntimeError("All selected islands belong to the same material")

            raw_uv_data = prepare_raw_uv_topo_data(self.p_context.uv_island_faces_list, self.p_context.face_to_verts, self.p_context.material_map)

            if prefs.write_to_file:
                out_filepath = os.path.join(tempfile.gettempdir(), 'uv_islands.data')
                out_file = open(out_filepath, 'wb')
                out_file.write(raw_uv_data)
                out_file.close()

            packer_args_final = [get_packer_path(), '-E', '-e', str(self.get_topo_analysis_level())] + self.get_packer_args()

            if prefs.multithreaded:
                packer_args_final.append('-t')

            if send_unselected:
                packer_args_final += ['-s', str(self.p_context.selected_count)]

            if in_debug_mode():
                if prefs.seed > 0:
                    packer_args_final += ['-S', str(prefs.seed)]

                if prefs.simplify_disable:
                    packer_args_final.append('-d')

                if prefs.benchmark:
                    packer_args_final.append('-b')

                packer_args_final += ['-T', str(prefs.test_param)]
                print('Pakcer args: ' + ' '.join(x for x in packer_args_final))

            self.packer_proc = subprocess.Popen(packer_args_final, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

            out_stream = self.packer_proc.stdin
            out_stream.write(raw_uv_data)
            out_stream.flush()

            self.packing_start_time = time.time()
            # Start progress monitor thread
            self.progress_queue = queue.Queue()
            self.connection_thread = threading.Thread(target=connection_thread_func,
                                                      args=(self.packer_proc.stdout, self.progress_queue))
            self.connection_thread.daemon = True
            self.connection_thread.start()
            self.curr_progress = 0
            self.progress_msg = ''
            self.pmsg_last_update = 0.0

            self.invalid_islands_msg = None
            self.island_flags_msg = None
            self.pack_solution_msg = None
            self.area_msg = None
            self.invalid_faces_msg = None
            self.similar_islands_msg = None

        except InconsistentMaterialError as err:
            self.report({'ERROR'}, 'Selected islands do not have unique material assigned')
            handle_invalid_islands(err.p_context, err.p_context.inconsistent_islands)
            cancel = True

        except RuntimeError as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, str(ex))
            cancel = True
        except Exception as ex:
            if in_debug_mode():
                print_backtrace(ex)

            self.report({'ERROR'}, 'Unexpected error')
            cancel = True

        self.p_context.update_meshes()

        if cancel:
            return {'FINISHED'}
        # context.scene.update()

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.1, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        self.confirmation_msg = self.get_confirmation_msg()

        wm = context.window_manager
        if self.confirmation_msg != '':
            return wm.invoke_props_dialog(self, width=700)

        return self.execute(context)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text=self.confirmation_msg)

    def get_confirmation_msg(self):
        return ''

    def send_unselected_islands(self):
        return False

    def prepare_material_map(self):
        return False


class UVP_OT_PackOperator(UVP_OT_PackOperatorGeneric):
    bl_idname = 'uv_packmaster.uv_pack'
    bl_label = 'Pack'
    bl_description = 'Pack selected UV islands'

    def send_unselected_islands(self):
        prefs = get_prefs()
        return prefs.FEATURE_pack_to_others and prefs.pack_to_others

    def prepare_material_map(self):
        prefs = get_prefs()
        return prefs.FEATURE_grouped_pack and prefs.grouped_pack and prefs.grouping_method == str(UvGroupingMethod.EXTERNAL)

    def process_result(self):
        prefs = get_prefs()
        overlap_detected = False

        if not prefs.FEATURE_demo:
            if self.pack_solution_msg is None:
                self.raiseUnexpectedOutputError()

            class IslandSolution:
                island_idx = None
                orient_angle = None
                orient_pivot = None
                orient_origin = None
                island_location = None

            solution_sizeX = force_read_float(self.pack_solution_msg)
            solution_sizeY = force_read_float(self.pack_solution_msg)

            if prefs.postscale_disable:
                solution_sizeX = 1.0
                solution_sizeY = 1.0

            solution_island_count = force_read_int(self.pack_solution_msg)

            island_solutions = []

            for i in range(solution_island_count):
                i_solution = IslandSolution()
                i_solution.island_idx = force_read_int(self.pack_solution_msg)

                floatArray = force_read_floats(self.pack_solution_msg, 7)

                i_solution.orient_angle = floatArray[0]
                i_solution.orient_pivot = mathutils.Vector(
                    (floatArray[1], floatArray[2],
                     0.0))
                i_solution.orient_origin = mathutils.Vector(
                    (floatArray[3], floatArray[4],
                     0.0))
                i_solution.island_location = mathutils.Vector(
                    (floatArray[5], floatArray[6],
                     0.0))

                island_solutions.append(i_solution)

            if self.island_flags_msg is None:
                self.raiseUnexpectedOutputError()

            island_flags = read_int_array(self.island_flags_msg)

            for i_solution in island_solutions:
                bm_idx = self.p_context.island_bm_map[i_solution.island_idx]
                bm = self.p_context.bms[bm_idx]
                uv_layer = self.p_context.uv_layers[bm_idx]
                face_idx_offset = self.p_context.face_idx_offsets[bm_idx]

                matrix = mathutils.Matrix.Translation(i_solution.island_location - i_solution.orient_origin) @ \
                         mathutils.Matrix.Translation(i_solution.orient_pivot) @ \
                         mathutils.Matrix.Rotation(i_solution.orient_angle, 4, 'Z') @ \
                         mathutils.Matrix.Translation(-i_solution.orient_pivot)

                island_faces = self.p_context.uv_island_faces_list[i_solution.island_idx]

                for face_idx in island_faces:
                    orig_face_idx = face_idx - face_idx_offset;
                    face = bm.faces[orig_face_idx]
                    for loop in face.loops:
                        uv = loop[uv_layer].uv
                        transformed_uv = matrix @ mathutils.Vector((uv[0], uv[1], 0.0))
                        loop[uv_layer].uv = (
                        transformed_uv[0] / solution_sizeX, transformed_uv[1] / solution_sizeY)

            overlap_detected = handle_island_flags(self.p_context, self.p_context.uv_island_faces_list, island_flags)

        if (self.packer_proc.returncode == UvPackerErrorCode.NO_SPACE):
            self.report({'WARNING'}, 'No enough space to pack all islands' + (
            ' (overlap check skipped)' if prefs.overlap_check else ''))
        elif overlap_detected:
            self.report({'WARNING'}, 'Packing is done, but overlapping islands were detected')
        else:
            report_msg = 'Packing done'
            if self.area_msg is not None:
                area = force_read_float(self.area_msg)
                report_msg = report_msg + ', packed islands area: ' + str(round(area, 4))
            self.report({'INFO'}, report_msg)

    def validate_pack_params(self):
        prefs = get_prefs()

        if prefs.FEATURE_heuristic_search and prefs.heuristic_search_time > 0 and len(self.p_context.uv_island_faces_list) < 2:
            raise RuntimeError("In order to use 'Heuristic Search' select more than one island")

        if prefs.FEATURE_pack_to_others and prefs.FEATURE_pack_ratio:
            if prefs.pack_to_others and prefs.tex_ratio:
                raise RuntimeError("'Pack To Others' is not supported with the 'Use Tex Ratio' option")

        if prefs.FEATURE_pack_to_others and prefs.FEATURE_heuristic_search:
            if prefs.pack_to_others and prefs.heuristic_search_time > 0:
                raise RuntimeError("'Pack To Others' is not supported with the 'Heuristic Search Time' option")

        if prefs.FEATURE_grouped_pack and prefs.grouped_pack and prefs.grouping_method == str(UvGroupingMethod.SIMILARITY):
            if prefs.FEATURE_pack_to_others and prefs.pack_to_others:
                raise RuntimeError("'Pack To Others' is not supported with grouping by similarity")

            if not prefs.rot_enable:
                raise RuntimeError("Island rotations must be enabled in order to group by similarity")

            if prefs.prerot_disable:
                raise RuntimeError("'Pre-Rotation Disable' option must be off in order to group by similarity")

    def get_packer_args(self):
        prefs = get_prefs()
        packer_args = ['-o', str(UvPackerOpcode.PACK), '-i', str(prefs.iterations), '-m',
                       str(prefs.margin)]

        if prefs.FEATURE_island_rotation and prefs.rot_enable:
            packer_args += ['-r', str(prefs.rot_step)]
            if prefs.prerot_disable:
                packer_args += ['-w']

        if prefs.FEATURE_packing_depth:
            packer_args += ['-p', str(prefs.packing_depth)]

        if prefs.FEATURE_heuristic_search:
            packer_args += ['-h', str(prefs.heuristic_search_time)]

            if prefs.FEATURE_advanced_heuristic and prefs.advanced_heuristic:
                packer_args.append('-H')

        if prefs.FEATURE_pack_ratio and prefs.tex_ratio:
            ratio = get_active_image_ratio(self.p_context.context)
            packer_args += ['-q', str(ratio)]

        if prefs.FEATURE_grouped_pack and prefs.grouped_pack:
            packer_args += ['-g', '-a', prefs.grouping_method]

            if prefs.grouping_method == str(UvGroupingMethod.SIMILARITY):
                packer_args += ['-I', str(prefs.similarity_threshold)]

        if prefs.FEATURE_lock_overlapping and prefs.lock_overlapping:
            packer_args += ['-l']

        if (prefs.FEATURE_pack_to_others and prefs.pack_to_others):
            packer_args += ['-x']

        if prefs.overlap_check:
            packer_args.append('-c')

        if prefs.area_measure:
            packer_args.append('-A')

        return packer_args


class UVP_OT_OverlapCheckOperator(UVP_OT_PackOperatorGeneric):
    bl_idname = 'uv_packmaster.uv_overlap_check'
    bl_label = 'Overlap Check'
    bl_description = 'Check wheter selected UV islands overlap each other'

    def process_result(self):
        prefs = get_prefs()

        if self.island_flags_msg is None:
            self.raiseUnexpectedOutputError()

        island_flags = read_int_array(self.island_flags_msg)
        overlap_detected = handle_island_flags(self.p_context, self.p_context.uv_island_faces_list, island_flags)

        if overlap_detected:
            self.report({'WARNING'}, 'Overlapping islands detected')
        else:
            self.report({'INFO'}, 'No overlapping islands detected')

    def validate_pack_params(self):
        pass

    def get_packer_args(self):
        prefs = get_prefs()
        packer_args = ['-o', str(UvPackerOpcode.OVERLAP_CHECK)]

        return packer_args



class UVP_OT_MeasureAreaOperator(UVP_OT_PackOperatorGeneric):
    bl_idname = 'uv_packmaster.uv_measure_area'
    bl_label = 'Measure Area'
    bl_description = 'Measure area of selected UV islands'

    def process_result(self):
        if self.area_msg is None:
            self.raiseUnexpectedOutputError()

        area = force_read_float(self.area_msg)
        self.report({'INFO'}, 'Islands area: ' + str(round(area, 4)))

    def validate_pack_params(self):
        pass

    def get_packer_args(self):
        prefs = get_prefs()

        packer_args = ['-o', str(UvPackerOpcode.MEASURE_AREA)]

        return packer_args



class UVP_OT_ValidateOperator(UVP_OT_PackOperatorGeneric):
    bl_idname = 'uv_packmaster.uv_validate'
    bl_label = 'Validate UVs'
    bl_description = 'Validate selected UV faces. The validation procedure looks for invalid UV faces i.e. faces with area close to 0, self-intersecting faces, faces overlapping each other'

    def get_confirmation_msg(self):
        prefs = get_prefs()

        if prefs.FEATURE_demo:
            return 'WARNING: in the demo mode only the number of invalid faces found is reported, invalid faces will not be selected. Click OK to continue'

        return ''

    def process_result(self):
        prefs = get_prefs()
        if self.invalid_faces_msg is None:
            self.raiseUnexpectedOutputError()

        invalid_face_count = force_read_int(self.invalid_faces_msg)
        invalid_faces = read_int_array(self.invalid_faces_msg)

        if not prefs.FEATURE_demo:
            if len(invalid_faces) != invalid_face_count:
                self.raiseUnexpectedOutputError()

            if invalid_face_count > 0:
                self.p_context.select_all_faces(False)
                self.p_context.select_faces(list(invalid_faces), True)
        else:
            if len(invalid_faces) > 0:
                self.raiseUnexpectedOutputError()

        if invalid_face_count > 0:
            self.report({'WARNING'}, 'Number of invalid faces found: ' + str(invalid_face_count))
        else:
            self.report({'INFO'}, 'No invalid faces found')

    def validate_pack_params(self):
        prefs = get_prefs()

        if not prefs.allow_self_intersect:
            raise RuntimeError("'Extended Topology Analysis' and 'Process Self-Intersecting UV Faces' options must be enabled in order to run validation")

        if self.p_context.context.tool_settings.use_uv_select_sync:
            for elem in self.p_context.bm.select_mode:
                if elem != 'FACE':
                    raise RuntimeError("Geometry selection mode must be set to FACE in order to run validation")
        else:
            if self.p_context.context.scene.tool_settings.uv_select_mode != 'FACE':
                raise RuntimeError("UV selection mode must be set to FACE in order to run validation")

    def get_packer_args(self):
        prefs = get_prefs()

        packer_args = ['-o', str(UvPackerOpcode.VALIDATE_UVS)]

        return packer_args

class UVP_OT_SelectSimilarOperator(UVP_OT_PackOperatorGeneric):
    bl_idname = 'uv_packmaster.uv_select_similar'
    bl_label = 'Select Similar'
    bl_description = "Select all islands which have a similar shape to already selected islands. See the description of the 'Similarity Threshold' parameter for more information"

    def get_confirmation_msg(self):
        prefs = get_prefs()

        if prefs.FEATURE_demo:
            return 'WARNING: in the demo mode only the number of similar islands found is reported, islands will not be selected. Click OK to continue'

        return ''

    def send_unselected_islands(self):
        return True

    def process_result(self):
        prefs = get_prefs()

        if self.similar_islands_msg is None:
            self.raiseUnexpectedOutputError()

        similar_island_count = force_read_int(self.similar_islands_msg)
        similar_islands = read_int_array(self.similar_islands_msg)

        if not prefs.FEATURE_demo:
            if len(similar_islands) != similar_island_count:
                self.raiseUnexpectedOutputError()

            for island_idx in similar_islands:
                self.p_context.select_island_faces(island_idx, self.p_context.uv_island_faces_list[island_idx], True)
        else:
            if len(similar_islands) > 0:
                self.raiseUnexpectedOutputError()

        self.report({'INFO'}, 'Similar islands found: ' + str(similar_island_count))

    def validate_pack_params(self):
        prefs = get_prefs()

        if not prefs.rot_enable:
            raise RuntimeError("Island rotations must be enabled in order to run operation")

        if prefs.prerot_disable:
            raise RuntimeError("'Pre-Rotation Disable' option must be off in order to run operation")

    def get_packer_args(self):
        prefs = get_prefs()

        packer_args = ['-o', str(UvPackerOpcode.SELECT_SIMILAR), '-I', str(prefs.similarity_threshold)]
        packer_args += ['-i', str(prefs.iterations)]

        if prefs.FEATURE_island_rotation and prefs.rot_enable:
            packer_args += ['-r', str(prefs.rot_step)]

        return packer_args