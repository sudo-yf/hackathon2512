from argus.agents.code_agent.code_parser import CodeParser


def test_code_parser_extracts_blocks():
    text = """
hello
```python
print(1)
```
```bash
echo ok
```
"""
    blocks = CodeParser(text)
    assert len(blocks) == 2
    assert blocks[0]["lang"] == "python"
    assert "print(1)" in blocks[0]["code"]
