from setuptools import setup, find_packages

setup(
    name="claudetask-mcp-bridge",
    version="1.0.0",
    py_modules=["claudetask_mcp_bridge"],
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.27",
        "pydantic>=2.5.0",
    ],
    entry_points={
        'console_scripts': [
            'claudetask-mcp-bridge=claudetask_mcp_bridge:main',
        ],
    },
    python_requires='>=3.8',
)