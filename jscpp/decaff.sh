#!/bin/bash

# decaff.sh
# decaffeinate javascript files
# place script in empty dir and run

#NPM_EXE=npm
NPM_EXE=pnpm

# assert a complete transform:
# file scripts/index.jsx
#   no more " : void 0" in ternary conditionals t?c:a
#   "<AceEditor" as jsx tag, no "React.createElement"

lebab_transforms=()
# Safe transforms:
lebab_transforms+=("arrow") # callback to arrow function
lebab_transforms+=("arrow-return") # drop return statements in arrow functions
lebab_transforms+=("for-of") # for loop to for-of loop
lebab_transforms+=("for-each") # for loop to Array.forEach()
lebab_transforms+=("arg-rest") # use of arguments to function(...args)
lebab_transforms+=("arg-spread") # use of apply() to spread operator
lebab_transforms+=("obj-method") # function values in objects to methods
lebab_transforms+=("obj-shorthand") # {foo: foo} to {foo}
lebab_transforms+=("no-strict") # remove "use strict" directives
lebab_transforms+=("exponent") # Math.pow() to ** operator (ES7)
lebab_transforms+=("multi-var") # single var x,y; declaration to var x; var y; (refactor)

# Unsafe transforms:
lebab_transforms+=("let") # var to let/const
lebab_transforms+=("class") # prototype assignments to class declaration
lebab_transforms+=("commonjs") # CommonJS module loading to import/export
lebab_transforms+=("template") # string concatenation to template string
lebab_transforms+=("default-param") # use of || to default parameters
#lebab_transforms+=("destruct-param") # use destructuring for objects in function parameters
lebab_transforms+=("includes") # indexOf() != -1 to includes() (ES7)

lebab_transform_str=''
for i in ${lebab_transforms[@]}
do
  lebab_transform_str+=",$i"
done
lebab_transform_str=${lebab_transform_str:1} # remove first comma
echo lebab_transform_str = $lebab_transform_str

true && {

	# install tools
  $NPM_EXE i -g \
  	coffee \
    prettier \
    eslint \
    eslint-plugin-react

  	#depercolate babel-cli \
    #babel-plugin-transform-react-createelement-to-jsx \
    #babel-plugin-transform-react-jsx \

	# install custom plugin for eslint
	$NPM_EXE i -g https://github.com/milahu/eslint-plugin-ternary-to-binary-conditional



	# JSCPP/master
  false && {
	  # get source
	  git clone --depth=1 https://github.com/felixhao28/JSCPP.git
	  cd JSCPP
	  # undo changes
	  git checkout origin/master --force
  }



  # JSCPP/gh-pages
  true && {

	  # get source
	  git clone --depth=1 https://github.com/felixhao28/JSCPP.git --branch gh-pages
	  mv -v JSCPP JSCPP_branch_gh-pages
	  cd JSCPP_branch_gh-pages

	  # undo changes
	  git checkout origin/gh-pages --force

		if [[ "$(git diff)" != "" ]]
		then
		  echo "error. 'git diff' is not empty"
		  exit 1
		fi

	}

}



done_js=()
done_jsx=()
old_out_files=()
git_add_force=()
done_failed=()

NL=$'\n'



eslint_config_file="eslintrc.$RANDOM.js";

cat >"$eslint_config_file" <<'EOF'

// eslintrc.js

module.exports = {
	env: {
		browser: true,
		es2020: true, // ES11
	},
  extends: [
  	'eslint:recommended',
  	'plugin:react/recommended',
  ],
  parserOptions: {
  	ecmaFeatures: {
  		jsx: true,
  	},
    ecmaVersion: 11,
    sourceType: 'module',
  },
  plugins: [
  	'ternary-to-binary-conditional',
  ],
  rules: { 
		'no-extra-parens': 'error',
		'react/jsx-curly-brace-presence': 'error',
		'no-void': 'error',
		'no-unused-expressions': 'error',
		'no-unneeded-ternary': 'error',
		'ternary-to-binary-conditional/ternary-to-binary-conditional': ['error', {
 			testExpression: "exprSrc === 'void 0'",
 		}],
 		
 		/*
 		'no-unused-vars': 'warn',
 		'no-undef': 'warn',
 		'react/no-deprecated': 'warn',
 		'react/react-in-jsx-scope': 'warn',
 		*/
  },
};

EOF



f_prettier_conf="prettier.config.temp${RANDOM}.js"
cat >"$f_prettier_conf" <<'EOF'

// prettier.config.js

// https://prettier.io/docs/en/options.html

module.exports = {

  singleQuote: true,

  // default config:

	//printWidth: 80,
  //tabWidth: 2,
  //useTabs: false,
  //semi: true,
  //quoteProps: "as-needed",
  //trailingComma: "es5",
  //bracketSpacing: true,

};

EOF



do_debug=false



# loop input files
# while read f; do ....; done < <( find .... )
while IFS= read -r -d '' f_input
do

  echo '============================================'

  f_input="${f_input:2}" # remove ./

  echo "f_input = $f_input"

  f_base="${f_input%.*}"

  # coffee -c: coffee -> js, cjsx -> jsx
  echo coffee to js
  js_es5="$(cat "$f_input" | coffee --compile --stdio --no-header --bare)"

  $do_debug && {
	  f_js_es5 = "$f_base.es5.temp${RANDOM}.js"
	  echo "write $f_js_es5"
	  echo "$js_es5" >"$f_js_es5"
	}

  # remove old file
  echo git rm
  git rm "$f_input"

  # test if output is JS or JSX code
  echo node check js
  if (echo "$js_es5" | node --check - >/dev/null 2>/dev/null)
  then
    out_ext='js'
    done_js+=("$f_input")
  else
    out_ext='jsx'
    done_jsx+=("$f_input")
  fi
  #f_out="${f_base}.es6.${out_ext}"
  f_out="${f_base}.${out_ext}"

  # lebab: es5 -> es6
  #lebab -o "$f_js_es6" "$f_js_es5"
  echo lebab
  js_es6="$(lebab -t $lebab_transform_str <(echo "$js_es5"))"

  # rename existing output file
  if [[ -f "$f_out" ]]
  then
    f_out_old="$f_out.old.temp${RANDOM}"
    cp -v "$f_out" "$f_out_old"
    old_out_files+=( "$f_out_old" )
    git rm "$f_out" || rm -v "$f_out"
  fi

  # write to file
  echo "write $f_out"
  echo "$js_es6" >"$f_out"

  # lint
  # eslint only works with files, not pipes (echo "$src" | eslint)
  echo eslint
  eslint_log="$f_base.eslint.error.log"
  eslint --fix --no-eslintrc --config "$eslint_config_file" "$f_out" 2>&1 >"$eslint_log" && {
  	echo eslint success
  	rm "$eslint_log"
  }

  # prettify
  echo prettier
  #js_pretty="$(echo "$js_linted" | prettier --stdin-filepath "$f_out")"
  prettier --write --config "$f_prettier_conf" "$f_out"

  # add new file
  echo git add
  git add "$f_out" || {
    # fore = ignore .gitignore
    git add --force "$f_out"
    git_add_force+=("$f_out")
  }

  # commit changes
  echo git commit
  git commit -m "cs2js ${f_out}${NL}${NL}old:  ${f_input}"

done < <( # bash process substitution so we can write to arrays
  find . -regextype posix-extended -regex '.*\.(coffee|cjsx)' -print0
)

echo '============================================'

rm "$f_prettier_conf"
rm "$eslint_config_file"

echo -e "\nold output files:"
for f in ${old_out_files[@]}; do echo "$f"; done

echo -e "\nconverted to js:"
for f in ${done_js[@]}; do echo "$f"; done

echo -e "\nconverted to jsx:"
for f in ${done_jsx[@]}; do echo "$f"; done

#echo -e "\nfailed:"
#for f in ${done_failed[@]}; do echo "$f"; done

echo -e "\nfiles added to git with force. check your .gitignore file:"
for f in ${git_add_force[@]}; do echo "$f"; done
