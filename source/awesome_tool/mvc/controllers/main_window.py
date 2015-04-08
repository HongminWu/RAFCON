import traceback

import gtk

from awesome_tool.mvc.controllers import GlobalVariableManagerController, StateMachineTreeController, LibraryTreeController
import awesome_tool.statemachine.singleton
from awesome_tool.mvc.controllers.extended_controller import ExtendedController
from awesome_tool.mvc.controllers.states_editor import StatesEditorController
from awesome_tool.mvc.controllers.state_machines_editor import StateMachinesEditorController
from awesome_tool.mvc.models.state_machine_manager import StateMachineManagerModel
from awesome_tool.mvc.selection import Selection
from awesome_tool.mvc.models.library_manager import LibraryManagerModel
from awesome_tool.mvc.shortcut_manager import ShortcutManager
from awesome_tool.mvc.views.state_machines_editor import StateMachinesEditorView
from awesome_tool.mvc.views.states_editor import StatesEditorView
from awesome_tool.utils import log
logger = log.get_logger(__name__)
import awesome_tool.statemachine.config
from awesome_tool.mvc.controllers.menu_bar_controller import MenuBarController
from awesome_tool.mvc.controllers.tool_bar_controller import ToolBarController
from awesome_tool.mvc.controllers.top_tool_bar_controller import TopToolBarController
from awesome_tool.utils import constants


class MainWindowController(ExtendedController):

    def __init__(self, state_machine_manager_model, view, gvm_model, editor_type='PortConnectionGrouped'):
        ExtendedController.__init__(self, state_machine_manager_model, view)

        self.editor_type = editor_type
        self.shortcut_manager = None

        # state machine manager
        assert isinstance(state_machine_manager_model, StateMachineManagerModel)
        state_machine_manager = state_machine_manager_model.state_machine_manager
        active_state_machine_id = state_machine_manager.active_state_machine_id
        active_state_machine = None
        if len(state_machine_manager_model.state_machines) > 0:
            active_state_machine = state_machine_manager_model.state_machines[active_state_machine_id]

        if active_state_machine is None:
            logger.warn("No active state machine found")

        # execution engine
        self.state_machine_execution_engine = awesome_tool.statemachine.singleton.state_machine_execution_engine
        self.observe_model(self.state_machine_execution_engine)
        self.state_machine_execution_engine.register_observer(self)

        ######################################################
        # shortcut manager
        ######################################################
        self.shortcut_manager = ShortcutManager(view['main_window'])

        ######################################################
        # logging view
        ######################################################
        self.console_scroller = view['console_scroller']
        view['debug_console_vbox'].remove(self.console_scroller)
        view.logging_view.get_top_widget().show()
        view['debug_console_vbox'].pack_start(view.logging_view.get_top_widget(), True, True, 0)

        ######################################################
        # library tree
        ######################################################
        library_manager_model = LibraryManagerModel(awesome_tool.statemachine.singleton.library_manager)
        library_controller = LibraryTreeController(library_manager_model, view.library_tree, state_machine_manager_model)
        self.add_controller('library_controller', library_controller)
        view['library_vbox'].remove(view['library_tree_placeholder'])
        view['library_vbox'].pack_start(view.library_tree, True, True, 0)
        # view['add_link_button'].connect("clicked", library_controller.add_link_button_clicked,
        #                                 state_machine_manager_model)
        # view['add_template_button'].connect("clicked", library_controller.add_template_button_clicked,
        #                                     state_machine_manager_model)
        view['add_link_menu_entry'].connect("activate", library_controller.add_link_button_clicked,
                                        state_machine_manager_model)
        view['add_template_menu_entry'].connect("activate", library_controller.add_template_button_clicked,
                                            state_machine_manager_model)

        view['main_window'].add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.BUTTON_MOTION_MASK |
                               gtk.gdk.KEY_PRESS_MASK | gtk.gdk.KEY_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)

        ######################################################
        # statemachine tree
        ######################################################
        # remove placeholder tab

        state_machine_tree_tab = view['state_machine_tree_placeholder']
        page_num = view["tree_notebook"].page_num(state_machine_tree_tab)
        view["tree_notebook"].remove_page(page_num)
        #append new tab
        #TODO: this is not always the active state machine
        state_machine_tree_controller = StateMachineTreeController(state_machine_manager_model, view.state_machine_tree)
        self.add_controller('state_machine_tree_controller', state_machine_tree_controller)
        state_machine_label = gtk.Label('STATE TREE')
        state_machine_event_box = gtk.EventBox()
        state_machine_event_box.set_border_width(constants.BORDER_WIDTH)
        state_machine_alignment = gtk.Alignment(0.0, 0.5, 0.0, 0.0)
        state_machine_alignment.add(state_machine_label)
        state_machine_event_box.add(state_machine_alignment)
        state_machine_tab_label = gtk.Label('State Tree')
        state_machine_vbox = gtk.VBox()
        state_machine_vbox.pack_start(state_machine_event_box, False, True, 0)
        state_machine_vbox.pack_start(view.state_machine_tree, True, True, 0)
        state_machine_vbox.show_all()
        view["tree_notebook"].insert_page(state_machine_vbox, state_machine_tab_label, page_num)

        ######################################################
        # state editor
        ######################################################
        states_editor_ctrl = StatesEditorController(state_machine_manager_model,  # or self.model,
                                                         view.states_editor,
                                                         editor_type)
        self.add_controller('states_editor_ctrl', states_editor_ctrl)
        ######################################################
        # state machines editor
        ######################################################
        state_machines_editor_ctrl = StateMachinesEditorController(state_machine_manager_model,
                                                                        view.state_machines_editor,
                                                                        states_editor_ctrl)
        self.add_controller('state_machines_editor_ctrl', state_machines_editor_ctrl)

        ######################################################
        # global variable editor
        ######################################################
        #remove placeholder tab
        global_variables_tab = view['global_variables_placeholder']
        page_num = view["tree_notebook"].page_num(global_variables_tab)
        view["tree_notebook"].remove_page(page_num)
        #append new tab
        global_variable_manager_ctrl = GlobalVariableManagerController(gvm_model, view.global_var_manager_view)
        self.add_controller('global_variable_manager_ctrl', global_variable_manager_ctrl)
        global_variables_label = gtk.Label('GLOBAL VARIABLES')
        global_variables_event_box = gtk.EventBox()
        global_variables_alignment = gtk.Alignment(0.0, 0.5, 0.0, 0.0)
        global_variables_alignment.add(global_variables_label)
        global_variables_event_box.add(global_variables_alignment)
        global_variables_event_box.set_border_width(constants.BORDER_WIDTH)
        global_variables_tab_label = gtk.Label('Global Variables')
        global_variables_vbox = gtk.VBox()
        global_variables_vbox.pack_start(global_variables_event_box, False, True, 0)
        global_variables_vbox.pack_start(view.global_var_manager_view.get_top_widget(), True, True, 0)
        global_variables_vbox.show_all()
        view["tree_notebook"].insert_page(global_variables_vbox, global_variables_tab_label, page_num)

        ######################################################
        # rotate all tab labels by 90 degrees
        ######################################################

        for i in range(view["tree_notebook"].get_n_pages()):
            child = view["tree_notebook"].get_nth_page(i)
            tab_label = view["tree_notebook"].get_tab_label(child)
            tab_label.set_angle(90)

        ######################################################
        # status bar
        ######################################################
        # add some data to the status bar
        status_bar1 = view["statusbar1"]
        status_bar1.push(0, "The awesome tool")
        status_bar2 = view["statusbar2"]
        status_bar2.push(0, "is awesome :-)")
        status_bar3 = view["statusbar3"]
        status_bar3_string = "Execution status: " + \
                             str(awesome_tool.statemachine.singleton.state_machine_execution_engine.status.execution_mode)
        status_bar3.push(0, status_bar3_string)

        ######################################################
        # menu bar
        ######################################################
        menu_bar_controller = MenuBarController(state_machine_manager_model,
                                                view,
                                                state_machines_editor_ctrl,
                                                states_editor_ctrl,
                                                view.logging_view,
                                                view.get_top_widget(),
                                                self.shortcut_manager)
        self.add_controller("menu_bar_controller", menu_bar_controller)

        ######################################################
        # tool bar
        ######################################################
        tool_bar_controller = ToolBarController(state_machine_manager_model,
                                                     view.tool_bar,
                                                     menu_bar_controller)
        self.add_controller("tool_bar_controller", tool_bar_controller)

        ######################################################
        # top tool bar
        ######################################################
        top_tool_bar_controller = TopToolBarController(state_machine_manager_model,
                                                     view.top_tool_bar,
                                                     view["main_window"],
                                                     menu_bar_controller)
        self.add_controller("top_tool_bar_controller", top_tool_bar_controller)

        ######################################################
        # setup correct sizes
        ######################################################
        view['top_level_h_pane'].set_position(1200)
        view['left_h_pane'].set_position(300)
        view['left_v_pane'].set_position(600)

    def register_view(self, view):
        self.register_actions(self.shortcut_manager)
        view['main_window'].connect('delete_event', self.get_controller("menu_bar_controller").on_delete_event)
        view['main_window'].connect('destroy', self.get_controller("menu_bar_controller").destroy)

    @ExtendedController.observe("execution_engine", after=True)
    def model_changed(self, model, prop_name, info):
        status_bar3 = self.view["statusbar3"]
        status_bar3_string = "Execution status: " + \
                             str(awesome_tool.statemachine.singleton.state_machine_execution_engine.status.execution_mode)
        status_bar3.push(0, status_bar3_string)