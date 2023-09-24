{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    utils,
  }: let
    supportedSystems = ["x86_64-linux" "aarch64-linux"];
  in
    utils.lib.eachSystem supportedSystems (system: let
      pkgs = import nixpkgs {inherit system;};
    in rec {
      formatter = pkgs.alejandra;

      packages.included-fonts = pkgs.runCommand "included-fonts" {} ''
        mkdir -p $out/share/fonts/{truetype,opentype}
        cp ${./fonts}/*.ttf $out/share/fonts/truetype
        cp ${./fonts}/*.otf $out/share/fonts/opentype
      '';

      devShell = with pkgs;
        mkShell {
          packages = [
            typst
            python3
            python3Packages.autopep8
            python3Packages.requests
          ];

          # We need CLDR main, not just the annotations
          CLDR_ROOT = pkgs.cldr-annotations.overrideAttrs (final: prev: {
            installPhase = ''
              runHook preInstall
              mkdir -p $out/share/unicode/cldr
              mv common $out/share/unicode/cldr
              runHook postInstall
            '';
          });

          TYPST_FONT_PATHS = with pkgs; symlinkJoin {
            name = "typst-fonts";
            paths = [
              packages.included-fonts
              noto-fonts-emoji
            ];
          };
        };
    });
}
