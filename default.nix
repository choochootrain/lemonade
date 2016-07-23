with import <nixpkgs> {}; with pkgs;

let
  enum34 = python35Packages.buildPythonPackage rec {
    name = "enum34-${version}";
    version = "1.1.6";
    src = fetchurl {
      url = "https://pypi.python.org/packages/bf/3e/31d502c25302814a7c2f1d3959d2a3b3f78e509002ba91aea64993936876/enum34-1.1.6.tar.gz";
      md5 = "5f13a0841a61f7fc295c514490d120d0";
    };
  };

  enum-compat = python35Packages.buildPythonPackage rec {
    name = "enum-compat-${version}";
    version = "0.0.2";
    propagatedBuildInputs = [ enum34 ];
    src = fetchurl {
      url = "https://pypi.python.org/packages/95/6e/26bdcba28b66126f66cf3e4cd03bcd63f7ae330d29ee68b1f6b623550bfa/enum-compat-0.0.2.tar.gz";
      md5 = "3002940b6620837d0fbc86ec72509be3";
    };
  };

  i3ipc = python35Packages.buildPythonPackage rec {
    name = "i3ipc-${version}";
    version = "1.2.0";
    propagatedBuildInputs = [ enum-compat ];
    src = fetchFromGitHub {
        owner = "acrisci";
        repo = "i3ipc-python";
        rev = "60afadf8b8c25effce933190070fa049edbf1842";
        sha256 = "1iza8j0aznhsbh5fddf2mb7a142rsc3819v1k7yylj333m6kyrxi";
    };
  };

  pythonEnv = python35.buildEnv.override {
    extraLibs = [ i3ipc ];
  };
in
stdenv.mkDerivation rec {
    name = "lemonade-${version}";
    version = "0.0.1";
    buildInputs = [ pythonEnv ];
}
