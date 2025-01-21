"""
    Builder for custom platform
"""

import os
import subprocess
from SCons.Script import DefaultEnvironment

env = DefaultEnvironment()

# Remove generic C/C++ tools
for k in ("CC", "CXX"):
    if k in env:
        del env[k]

# Preserve C and C++ build flags
backup_cflags = env.get("CFLAGS", [])
backup_cxxflags = env.get("CXXFLAGS", [])

def find_top_level_cmake(root_dir):
    """
    Search for the top-level CMakeLists.txt file within the src directory.
    """
    cmake_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "CMakeLists.txt" in filenames:
            cmake_files.append(os.path.join(dirpath, "CMakeLists.txt"))
    if not cmake_files:
        raise FileNotFoundError("No CMakeLists.txt found in the src directory")

    # Sort by path length to find the top-level CMakeLists.txt
    top_level_cmake = sorted(cmake_files, key=lambda x: len(x.split(os.sep)))[0]
    return top_level_cmake

def configure_and_build(cmake_file):
    """
    Configure and build the project using CMake.
    """
    build_dir = os.path.join(os.path.dirname(cmake_file), "build")

    # Create build directory if it doesn't exist
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    print(f"Configuring CMake project in {build_dir}...")
    try:
        # Configure CMake
        subprocess.run(
            ["cmake", "-B", build_dir, "-S", os.path.dirname(cmake_file)],
            check=True
        )
        print("CMake configuration successful")

        # Build the project
        print("Building the project...")
        subprocess.run(
            ["cmake", "--build", build_dir],
            check=True
        )
        print("CMake build successful")
    except subprocess.CalledProcessError as e:
        print(f"Error during CMake process: {e}")
        raise

# Find the top-level CMakeLists.txt in the src directory
src_dir = os.path.join(env.subst("$PROJECT_DIR"), "src")
print(f"Searching for CMakeLists.txt in {src_dir}...")
try:
    cmake_file = find_top_level_cmake(src_dir)
    print(f"Top-level CMakeLists.txt found at: {cmake_file}")

    # Configure and build the project
    configure_and_build(cmake_file)

except FileNotFoundError as e:
    print(e)
    print("Aborting build process due to missing CMakeLists.txt.")
