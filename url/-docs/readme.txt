-------------------------------------------------
  Code Canopy URL Shortner  V2.0
-------------------------------------------------

	Install	
----------------------

1. Upload all files.

2. chmod /lib to 777 (allow all)

3. visit url and follow instructions on screen.

4. Your done your site is ready!







For those who can not see .htaccess here are the file contents:


RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule   ^stats/(.*) /info.php?short=$1 [L]

RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule   ^(.*) /forward.php?$1 [L]