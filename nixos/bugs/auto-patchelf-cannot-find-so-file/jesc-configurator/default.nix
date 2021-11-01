/*
nix-build -E 'with import <nixpkgs> { }; callPackage ./default.nix { }'

discussion
https://discourse.nixos.org/t/autopatchhelfhook-could-not-satisfy-dependencies/13745

default.nix based on
https://gist.github.com/beezow/9c428f2715d7e94054c1f47a763294f1
*/

{lib, stdenv, fetchurl, unzip, makeDesktopItem, copyDesktopItems
, nwjs
, nwjs-sdk
, autoPatchelfHook
, wrapGAppsHook, gsettings-desktop-schemas, gtk3 }:

let
  pname = "jesc-configurator";
  desktopItem = makeDesktopItem {
    name = pname;
    exec = pname;
    icon = pname;
    comment = "JESC configuration tool";
    desktopName = "JESC Configurator";
    genericName = "ESC configuration tool";
  };
in
stdenv.mkDerivation rec {
  inherit pname;
  version = "1.2.9";
  src = fetchurl {
    url = "https://github.com/jflight-public/jesc-configurator/releases/download/v${version}/JESC-Configurator_linux64_${version}.zip";
    sha256 = "704f63f4d6e05d9ac28bde73deeafb4119a8200c68029087e1453bd62431934f";
  };

  nativeBuildInputs = [ 
    unzip
    copyDesktopItems
    autoPatchelfHook
  ];

  buildInputs = [ nwjs-sdk gsettings-desktop-schemas gtk3 ];

  installPhase = ''
    mkdir -p $out/bin
    cp "jesc-configurator" $out/bin

    # redefine findDependency
    # based on https://github.com/NixOS/nixpkgs/blob/master/pkgs/build-support/setup-hooks/auto-patchelf.sh
    findDependency() {
        local filename="$1"
        local arch="$2"
        local osabi="$3"
        local lib dep
        echo
        echo "debug findDependency: filename = $filename"
        echo "debug findDependency:   arch = $arch"
        echo "debug findDependency:   osabi = $osabi"

        if [ $depCacheInitialised -eq 0 ]; then
            for lib in "''${autoPatchelfLibs[@]}"; do
                echo "debug findDependency: cache: add lib = $lib"
                for so in "$lib/"*.so*; do
                  echo "debug findDependency: cache:   add $(basename "$so") = $so"
                  addToDepCache "$so"
                done
            done
            depCacheInitialised=1
        fi

        for dep in "''${autoPatchelfCachedDeps[@]}"; do
            if [ "$filename" = "''${dep##*/}" ]; then
                echo "debug findDependency: candidate by filename: dep = $dep"
                echo "debug findDependency:   arch = $(getBinArch "$dep") - expected $arch"
                echo "debug findDependency:   osabi = $(getBinOsabi "$dep") - expected $osabi"
                if [ "$(getBinArch "$dep")" = "$arch" ] && areBinOsabisCompatible "$osabi" "$(getBinOsabi "$dep")"; then
                    foundDependency="$dep"
                    return 0
                fi
            fi
        done

        # Populate the dependency cache with recursive dependencies *only* if we
        # didn't find the right dependency so far and afterwards run findDependency
        # again, but this time with $doneRecursiveSearch set to 1 so that it won't
        # recurse again (and thus infinitely).
        if [ $doneRecursiveSearch -eq 0 ]; then
            populateCacheWithRecursiveDeps
            doneRecursiveSearch=1
            findDependency "$filename" "$arch" || return 1
            return 0
        fi
        return 1
    }

  '';
}
