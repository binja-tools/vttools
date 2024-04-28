from binaryninja import *
from binaryninja.plugin import PluginCommand

def def_vt_fn(bv, start, length):
    user_input = get_text_line_input("Enter type name", "Vtable this pointer type")
    if user_input is None:
        print("Nothing to do")
        return
    user_input = user_input.decode()
    user_input = user_input.strip()
    if user_input[-1] != '*':
        user_input += '*'
    new_param_type = bv.parse_type_string(user_input)[0]
    with bv.undoable_transaction():
        for i in range(start, start + length, 8):
            fn = bv.get_data_var_at(i).value
            func = bv.get_function_at(fn)
            new_param = FunctionParameter(new_param_type, "self")
            new_params = []
            new_params.append(new_param)
            for param in func.type.parameters[1:]:
                new_params.append(param)
            type_ = func.type
            new_func = FunctionType.create(
                ret = type_.return_value,
                params = new_params,
                calling_convention = type_.calling_convention,
                variable_arguments = type_.has_variable_arguments,
                stack_adjust = type_.stack_adjustment,
                can_return = type_.can_return,
                pure = type_.pure
            )
            func.set_user_type(new_func)
            func.mark_updates_required()
            func.mark_caller_updates_required()
            func.reanalyze()

PluginCommand.register_for_range(
    "VtTools\Define Vt Fn",
    "Sets the first argument of all functions in range to given type",
    def_vt_fn
)
