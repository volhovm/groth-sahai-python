#( let
#    my_toolz = python38.pkgs.buildPythonPackage rec {
#      pname = "toolz";
#      version = "0.10.0";
#
#      src = python38.pkgs.fetchPypi {
#        inherit pname version;
#        sha256 = "08fdd5ef7c96480ad11c12d472de21acd32359996f69a5259299b540feba4560";
#      };
#
#      doCheck = false;
#
#      meta = {
#        homepage = "https://github.com/pytoolz/toolz/";
#        description = "List processing tools and functional utilities";
#      };
#    };
#
#  in python38.withPackages (ps: [ps.numpy my_toolz])

with import <nixpkgs> {};
( let
    pypkgs = python39.pkgs;

    eth-typing = pypkgs.buildPythonPackage rec {
      pname = "eth-typing";
      version = "2.2.2";

      src = pypkgs.fetchPypi {
        inherit pname version;
        sha256 = "0gvzhwhhk8nl0rgbyqi7amn0fs0iya1lkmbfixkd7wbwva1hzflp";
      };
      doCheck = false;

#      checkInputs = [ pypkgs.cytoolz ];
#      propagatedBuildInputs = [ pypkgs.cytoolz ];

      meta = {
        homepage = "https://github.com/ethereum/eth-typing/";
        description = "eth typing";
      };
    };


    eth-hash = pypkgs.buildPythonPackage rec {
      pname = "eth-hash";
      version = "0.3.2";

      src = pypkgs.fetchPypi {
        inherit pname version;
        sha256 = "0xjskfa1b11gb4pi1i88h5r07waps0czq2jmm551i25dbv6wwh1z";
      };
      doCheck = false;

#      checkInputs = [ pypkgs.cytoolz ];
#      propagatedBuildInputs = [ pypkgs.cytoolz ];

      meta = {
        homepage = "https://github.com/ethereum/eth-hash/";
        description = "eth hash";
      };
    };


    eth-utils = pypkgs.buildPythonPackage rec {
      pname = "eth-utils";
      version = "1.10.0";

      src = pypkgs.fetchPypi {
        inherit pname version;
        sha256 = "1bv19ig3gsl5y3333amdy39m9ja8f5d2cw031cci91wp8qm7d0mz";
      };
      doCheck = false;

      checkInputs = [ pypkgs.cytoolz eth-hash eth-typing ];
      propagatedBuildInputs = [ pypkgs.cytoolz eth-hash eth-typing ];

      meta = {
        homepage = "https://github.com/ethereum/eth-utils/";
        description = "eth utils";
      };
    };

    py_ecc = pypkgs.buildPythonPackage rec {
      pname = "py_ecc";
      version = "5.2.0";

      src = pypkgs.fetchPypi {
        inherit pname version;
#        sha256 = "08fdd5ef7c96480ad11c12d472de21acd32359996f69a5259299b540feba4511";
        sha256 = "1fk4xnfg7isvbgql5fnzpsb1mzwm0a2y6c85bvkv5v0k534bvaph";
      };

      doCheck = false;

      checkInputs = [ pypkgs.mypy-extensions eth-utils pypkgs.cached-property ];
      propagatedBuildInputs = [ pypkgs.mypy-extensions pypkgs.cytoolz eth-utils pypkgs.cached-property pypkgs.setuptools ];

      meta = {
        homepage = "https://github.com/ethereum/py_ecc/";
        description = "PY ECC library";
      };
    };

  in {
     pythonEnv = stdenv.mkDerivation {
       name = "python-env";
       buildInputs = [
         (python39.withPackages (ps: [ps.numpy py_ecc]))
         ];
     };
  }
)
