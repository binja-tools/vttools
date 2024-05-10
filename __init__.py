from binaryninja import *
from binaryninja.plugin import PluginCommand
import sys

def def_vt_fn(bv, start, length):
    user_input = get_text_line_input("Enter type name", "Vtable this pointer type")
    if user_input is None:
        print("Nothing to do")
        return
    user_input = user_input.decode()
    user_input = user_input.strip()
    try:
        new_param_type = bv.parse_type_string(user_input)[0]
    except:
        print(f"type {user_input} not found", file=sys.stderr)
        return
    first_reg = bv.platform.calling_conventions[0].int_arg_regs[0]
    param1 = bv.arch.regs[first_reg]
    if new_param_type.width > param1.size:
        print(f"type {user_input} does not fit into register {first_reg}", file=sys.stderr)
        return
    try:
        with bv.undoable_transaction():
            for i in range(start, start + length, 8):
                fn = bv.read_pointer(i)
                func = bv.get_function_at(fn)
                new_param = FunctionParameter(new_param_type, "self")
                new_params = []
                new_params.append(new_param)
                if func is None or func.type is None:
                    print(hex(i), "is not a function ptr", file=sys.stderr)
                    raise
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
    except:
        pass

PluginCommand.register_for_range(
    "VtTools\\Define Vt Fn",
    "Sets the first argument of all functions in range to given type",
    def_vt_fn
)
