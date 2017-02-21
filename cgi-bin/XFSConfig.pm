package XFSConfig;
use strict;
use lib 'Modules';
use Exporter ();
@XFSConfig::ISA    = qw(Exporter);
@XFSConfig::EXPORT = qw($c);
use vars qw( $c );

$c=
{
 # Directory for temporary using files, witout trailing /
 temp_dir => '/home4/filesrus/public_html/cgi-bin/temp',

 # Directory for uploaded files, witout trailing /
 upload_dir => '/home4/filesrus/public_html/cgi-bin/uploads',

 cgi_dir => '',

 # Path to htdocs/files folder - to generate direct links, witout trailing /
 htdocs_dir => '/home4/filesrus/public_html/files',

 # Path to htdocs/tmp folder
 htdocs_tmp_dir => '',

 # FileServer auth key (generating when adding server)
 fs_key => '',

 dl_key => '',

 # FileServer status
 srv_status => 'ON',

 # Your Main site URL, witout trailing /
 site_url => 'http://filesrush.com',

 # Your Main site cgi-bin URL, witout trailing /
 site_cgi => 'http://filesrush.com/cgi-bin',

 m_i => '',
 m_v => '',
 m_r => '',
 
 mu_logins => '',
 nl_logins => '',
 hf_logins => '',

 m_i_resize => '0',

 bitflu_address => '127.0.0.1:4081',


#--- Anonymous users limits ---#
 enabled_anon => '1',

 # Max number of upload fields
 max_upload_files_anon => '2',

 # Maximum upload Filesize in Mbytes (0 to disable)
 max_upload_filesize_anon => '1000',

 # Allow remote URL uploads
 remote_url_anon => '1',
#------#

#--- Registered users limits ---#
 enabled_reg => '1',

 # Max number of upload fields
 max_upload_files_reg => '3',

 # Maximum upload Filesize in Mbytes (0 to disable)
 max_upload_filesize_reg => '500',

 # Allow remote URL uploads
 remote_url_reg => '1',
#------#

#--- Premium users limits ---#
 enabled_prem => '1',

 # Max number of upload fields
 max_upload_files_prem => '5',

 # Maximum upload Filesize in Mbytes (0 to disable)
 max_upload_filesize_prem => '1000',

 # Allow remote URL uploads
 remote_url_prem => '1',
#------#

 # Banned IPs
 # Use \d+ for wildcard *
 ip_not_allowed => '',

 # Logfile name
 uploads_log => 'logs.txt',

 # Enable scanning file for viruses with ClamAV after upload (Experimental)
 # You need ClamAV installed on your server
 enable_clamav_virus_scan => '0',

 # Update progress bar using streaming method
 ajax_stream => 0,

 #Files per dir, do not touch since server start
 files_per_folder => 5000,

##### Custom error messages #####

 msg => { upload_size_big   => "Maximum total upload size exceeded<br>Max total upload size is: ",
          file_size_big     => "Max filesize limit exceeded! Filesize limit: ",
          no_temp_dir       => "No temp dir exist! Please fix your temp_dir variable in config.",
          no_target_dir     => "No target dir exist! Please fix your target_dir variable in config.",
          transfer_complete => "Transfer complete!",
          transfer_failed   => "Upload failed!",
          null_filesize     => "have null filesize or wrong file path",
          bad_filename      => "is not acceptable filename! Skipped.",
          too_many_files    => "wasn't saved! Number of files limit exceeded.",
          saved_ok          => "saved successfully.",
          wrong_password    => "You've entered wrong password.<br>Authorization required.",
          ip_not_allowed    => "You are not allowed to upload files",
        },

 ### NEW 1.7 ###
 m_i_width => '200',
 m_i_height => '200',
 m_i_wm_position => '',
 m_i_wm_image => '',

 m_h_login => '',
 m_h_password => '',
 fs_files_url => '',
 fs_cgi_url => '',

 ### NEW 1.8 ###
 m_h => '',

 m_e => '',
 m_e_vid_width => '',
 m_e_vid_quality => '',
 m_e_audio_bitrate => '',

 rs_logins => '',
 mf_logins => '',
 fs_logins => '',
 df_logins => '',
 ff_logins => '',
 es_logins => '',
 sm_logins => '',
 ug_logins => '',
 fe_logins => '',

 m_i_hotlink_orig => '',

 m_b => '',
};

1;
