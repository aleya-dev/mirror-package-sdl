from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import rmdir, rm, collect_libs
import os


required_conan_version = ">=2.0"


class SDL2Conan(ConanFile):
    name = "sdl"
    version = "3.1.2"
    python_requires = "aleya-conan-base/1.3.0@aleya/public"
    python_requires_extend = "aleya-conan-base.AleyaConanBase"
    ignore_cpp_standard = True

    exports_sources = "source/*"

    options = {
        "shared": [False, True],
        "fPIC": [False, True]
    }

    default_options = {
        "shared": False,
        "fPIC": True
    }

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SDL_SHARED"] = self.options.shared
        tc.variables["SDL_STATIC"] = not self.options.shared
        tc.variables["SDL_TESTS"] = False
        tc.variables["SDL_TEST_LIBRARY"] = False
        tc.variables["SDL_STATIC_VCRT"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        rmdir(self, os.path.join(self.package_folder, "share"))
        rmdir(self, os.path.join(self.package_folder, "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "aclocal"))
        rmdir(self, os.path.join(self.package_folder, "licenses"))
        rm(self, "*.pdb", os.path.join(self.package_folder, "lib"), recursive=False)
        rm(self, "sdl2-config", os.path.join(self.package_folder, "bin"), recursive=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "SDL3")

        self.cpp_info.components["sdl3"].libs = collect_libs(self)
        self.cpp_info.components["sdl3"].set_property("cmake_target_name", "SDL3::SDL3")

        if self.settings.os == "Windows":
            self.cpp_info.components["sdl3"].system_libs = \
                ["user32", "gdi32", "winmm", "imm32", "ole32",
                 "oleaut32", "version", "uuid", "advapi32", "setupapi", "shell32"]

        if self.settings.os == "Linux":
            self.cpp_info.components["sdl3"].system_libs = \
                ["m", "dl", "rt", "pthread", "X11", "Xrandr", "Xi", "Xxf86vm"]

        if self.settings.os == "Macos":
            self.cpp_info.components["sdl3"].frameworks = \
                ["Carbon",
                 "AppKit",
                 "Metal",
                 "ForceFeedback",
                 "GameController",
                 "Foundation",
                 "CoreServices",
                 "CoreFoundation",
                 "CoreVideo",
                 "CoreGraphics",
                 "CoreHaptics",
                 "CoreAudio",
                 "AudioToolbox"]

        self.cpp_info.components["headers"].libs = []
        self.cpp_info.components["headers"].libdirs = []
        self.cpp_info.components["headers"].set_property("cmake_target_name", "SDL3::Headers")
