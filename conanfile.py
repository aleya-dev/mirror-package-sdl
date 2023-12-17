from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import rmdir, rm, replace_in_file
import os


required_conan_version = ">=2.0"


class SDL2Conan(ConanFile):
    name = "sdl"
    version = "2.28.5"
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

    def _patch_sources(self):
        cmakelists = os.path.join(self.source_folder, "CMakeLists.txt")
        if self.settings.os == "Macos":
            # don't check for iconv at all
            replace_check = "#check_library_exists(iconv iconv_open"
            replace_in_file(self, cmakelists, "check_library_exists(iconv iconv_open",
                            replace_check)

        # Avoid assuming iconv is available if it is provided by the C runtime,
        # and let SDL build the fallback implementation
        replace_in_file(self, cmakelists,
                        'check_library_exists(c iconv_open "" HAVE_BUILTIN_ICONV)',
                        '# check_library_exists(c iconv_open "" HAVE_BUILTIN_ICONV)')

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["SDL_SHARED"] = self.options.shared
        tc.variables["SDL_STATIC"] = not self.options.shared
        tc.variables["SDL_TEST"] = False
        tc.variables["SDL_TESTS"] = False
        tc.generate()

    def build(self):
        self._patch_sources()
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
        rm(self, "sdl2-config", os.path.join(self.package_folder, "bin"), recursive=False)

    def package_info(self):
        postfix = "d" if self.settings.os != "Android" and self.settings.build_type == "Debug" else ""
        static_postfix = "-static" if not self.options.shared and self.settings.os == "Windows" else ""

        self.cpp_info.set_property("cmake_file_name", "SDL2")

        self.cpp_info.components["libsdl2"].libs = ["SDL2" + static_postfix + postfix]
        self.cpp_info.components["libsdl2"].set_property("cmake_target_name", "SDL2::SDL2")

        if self.settings.os == "Windows":
            self.cpp_info.components["libsdl2"].system_libs = \
                ["user32", "gdi32", "winmm", "imm32", "ole32",
                 "oleaut32", "version", "uuid", "advapi32", "setupapi", "shell32"]

        if self.settings.os == "Linux":
            self.cpp_info.components["libsdl2"].system_libs = \
                ["dl", "rt", "pthread", "X11", "Xrandr", "Xi", "Xxf86vm"]

        if self.settings.os == "Macos":
            self.cpp_info.components["libsdl2"].frameworks = \
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

        self.cpp_info.components["sdl2main"].libs = ["SDL2main" + postfix]
        self.cpp_info.components["sdl2main"].set_property("cmake_target_name", "SDL2::SDL2main")
        self.cpp_info.components["sdl2main"].requires = ["libsdl2"]
