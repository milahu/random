#!/usr/bin/python3

# diff-lazy.py
# produce a more 'lazy' output than gnu diff -u
# aka lazy diff, or less-greedy diff

#todo implement -p flag in difflib = show C function name
#todo add a 'lazy' flag to gnu diff

# license = Unlicense = public domain
# author = milahu

'''
example
f1.c:
bool foo_function()
{
#ifdef FOO_CONFIG
	return true;
#else
	return false;
#endif
}
f2.c:
#ifdef FOO_CONFIG
bool foo_variable = true;
#else
bool foo_variable = false;
#endif
bool foo_function()
{
	return foo_variable;
}
gnu diff:
diff -u --label f1.c --label f2.c f1.c f2.c 
--- f1.c
+++ f2.c
@@ -1,8 +1,9 @@
-bool foo_function()
-{
 #ifdef FOO_CONFIG
-	return true;
+bool foo_variable = true;
 #else
-	return false;
+bool foo_variable = false;
 #endif
+bool foo_function()
+{
+	return foo_variable;
 }
python diff:
difflib.unified_diff
--- f1.c
+++ f2.c
@@ -1,8 +1,9 @@
+#ifdef FOO_CONFIG
+bool foo_variable = true;
+#else
+bool foo_variable = false;
+#endif
 bool foo_function()
 {
-#ifdef FOO_CONFIG
-	return true;
-#else
-	return false;
-#endif
+	return foo_variable;
 }
'''

import sys
import difflib

def my_diff(f, f2=None):
	if not f2:
		# guess original file
		f1 = f + '.orig'
		f2 = f
		# git diff naming
		n1 = 'a/' + f
		n2 = 'b/' + f
	else:
		f1 = f
		#f2 = f2
		n1 = f1
		n2 = f2
	return ''.join(
		difflib.unified_diff(
			open(f1, 'r').readlines(),
			open(f2, 'r').readlines(),
			fromfile=n1, # label
			tofile=n2, # label
			lineterm='\n'
		)
	)

if __name__ == '__main__':
	argc = len(sys.argv) - 1
	if argc == 1:
		print(my_diff(sys.argv[1]))
	elif argc == 2:
		print(my_diff(sys.argv[1], sys.argv[2]))
	else:
		print('usage: ' + sys.argv[0] + ' f [f2]')
		print('f      --> f.orig vs f')
		print('f + f2 --> f      vs f2')
