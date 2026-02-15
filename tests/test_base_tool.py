from argus.tools.base_tool import FunctionTool


def test_function_tool_executes_dict_result():
    tool = FunctionTool(
        name="sum",
        description="sum values",
        parameters_schema={
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
        },
        execute_func=lambda a, b: {"success": True, "value": a + b},
    )

    valid, error = tool.validate_parameters({"a": 1, "b": 2})
    assert valid and error is None
    assert tool.execute(a=1, b=2)["value"] == 3
