package XFileConfig;
use strict;
use lib 'Modules';
use Exporter;
@XFileConfig::ISA    = qw(Exporter);
@XFileConfig::EXPORT = qw($c);
use vars qw( $c );

$c=
{
 license_key => '',

 # MySQL settings
 db_host => 'localhost',
 db_login => 'filesrus_xfsuser',
 db_passwd => 'Mz[5PktOGCtx',
 db_name => 'filesrus_xfsfiles',

 default_language => 'english',

 # Passwords crypting random salt. Set it up once when creating system
 pasword_salt  => 'ey7w58unrpfe',

 # Secret key to crypt Download requests
 dl_key => 'SECRETKEY182',

 # Your site name that will appear in all templates
 site_name => 'Filesrush',

 # Your site URL, witout trailing /
 site_url => 'http://filesrush.com',

 # Your site cgi-bin URL, witout trailing /
 site_cgi => 'http://filesrush.com/cgi-bin',

 # Path to your site htdocs folder
 site_path => '/home4/filesrus/public_html',

 cgi_path => '',

 # Delete Direct Download Links after X hours
 symlink_expire => '8', # hours

 # Do not expire premium user's files
 dont_expire_premium => '1',

 # Generated links format, 0-5
 link_format => '5',

 enable_catalogue => '1',

 # Allowed file extensions delimited with '|'
 # Leave blank to allow all extensions
 # Sample: 'jpg|gif',
 ext_allowed => '',

 # Not Allowed file extensions delimited with '|'
 # Leave it blank to disable this filter
 # Sample: 'exe|com'
 ext_not_allowed => '',

 # Banned IPs
 # Examples: '^(10.0.0.182)$' - ban 10.0.0.182, '^(10.0.1.125|10.0.0.\d+)$' - ban 10.0.1.125 & 10.0.0.*
 # Use \d+ for wildcard *
 ip_not_allowed => '',

 # Banned filename parts
 fnames_not_allowed => '(warez|porno|crack)',

 # Use captcha verification to avoid robots
 # 0 - disable captcha, 1 - image captcha (requires GD perl module installed), 2 - text captha, 3 - reCaptcha
 captcha_mode => '2',

 # Enable users to add descriptions to files
 enable_file_descr => '1',

 # Allow users to add comments to files
 enable_file_comments => '1',

 # Replace all chars except "a-zA-Z0-9.-" with underline
 sanitize_filename => '',

 # Enable page with Premium/Free download choice
 pre_download_page => '1',

 # Used for BW limit
 bw_limit_days => '3',

 charset => 'UTF-8',

 # Require e-mail registration
 registration_confirm_email => '1',

 # Mail servers not allowed for registration
 # Sample: 'mailinator.com|gmail.com'
 mailhosts_not_allowed => '(mailinator.com|yopmail.com)',

 # Reject comments with banned words
 bad_comment_words => '(fuck|shit)',

 # Add postfix to filename
 add_filename_postfix => '',

 # Show images instantly
 image_mod => '1',

 # Don't show Download button when showing image
 image_mod_no_download => '1',

 # Play mp3 files instantly
 mp3_mod => '1',

 # Don't show Download button when showing mp3 player
 mp3_mod_no_download => '',

 # Don't show Download button when showing video player
 video_mod_no_download => '',

 # Keys used for reCaptcha
 recaptcha_pub_key => '',
 recaptcha_pri_key => '',

 m_i => '',
 m_v => '',
 m_r => '',
 
 mu_logins => '',
 nl_logins => '',
 hf_logins => '',

 ping_google_sitemaps => '1',

 # Show last news in header for X days after addition
 show_last_news_days => '0',

 m_v_page => '1',

 # Check IP on download: exact, first3, first2, all
 link_ip_logic => 'exact',

#--- Anonymous users limits ---#

 # Enable anonymous upload
 enabled_anon => '1',

 # Max number of upload fields
 max_upload_files_anon => '2',

 # Maximum upload Filesize in Mbytes (0 to disable)
 max_upload_filesize_anon => '100',

 # Maximum number of downloads for single file (0 to disable)
 max_downloads_number_anon => '200',

 # Specify number of seconds users have to wait before download, 0 to disable
 download_countdown_anon => '5',

 # Captcha for downloads
 captcha_anon => '1',

 # Show advertisement
 ads_anon => '1',

 # Limit Max bandwidth for IP per 'bw_limit_days' days
 bw_limit_anon => '5000',

 # Add download delay per 100 Mb file, seconds
 add_download_delay_anon => '0',

 # Allow remote URL uploads
 remote_url_anon => '',

 # Generate direct links
 direct_links_anon => '1',

 # Download speed limit, Kbytes/s
 down_speed_anon => '',

 # Maximum download size in Mbytes (0 to disable) 
 max_download_filesize_anon => '100',
#------#

#--- Registered users limits ---#

 # Enable user registration
 enabled_reg => '1',

 # Max number of upload fields
 max_upload_files_reg => '3',

 # Maximum disk space in Mbytes (0 to disable)
 disk_space_reg => '10000',

 # Maximum upload Filesize in Mbytes (0 to disable)
 max_upload_filesize_reg => '500',

 # Maximum number of downloads for single file (0 to disable)
 max_downloads_number_reg => '500',

 # Specify number of seconds users have to wait before download, 0 to disable
 download_countdown_reg => '3',

 # Captcha for downloads
 captcha_reg => '',

 # Show advertisement
 ads_reg => '1',

 # Limit Max bandwidth for IP per 'bw_limit_days' days
 bw_limit_reg => '8000',

 # Add download delay per 100 Mb file, seconds
 add_download_delay_reg => '0',

 # Allow remote URL uploads
 remote_url_reg => '1',

 # Generate direct links
 direct_links_reg => '1',

 # Download speed limit, Kbytes/s
 down_speed_reg => '',

 # Maximum download size in Mbytes (0 to disable) 
 max_download_filesize_reg => '500',

 max_rs_leech_reg => '300',

 torrent_dl_reg => '1',

#------#

#--- Premium users limits ---#

 # Enable premium accounts
 enabled_prem => '1',

 # Max number of upload fields
 max_upload_files_prem => '5',

 # Maximum disk space in Mbytes (0 to disable)
 disk_space_prem => '50000',

 # Maximum upload Filesize in Mbytes (0 to disable)
 max_upload_filesize_prem => '1000',

 # Maximum number of downloads for single file (0 to disable)
 max_downloads_number_prem => '0',

 # Specify number of seconds users have to wait before download, 0 to disable
 download_countdown_prem => '0',

 # Captcha for downloads
 captcha_prem => '',

 # Show advertisement
 ads_prem => '1',

 # Limit Max bandwidth for IP per 'bw_limit_days' days
 bw_limit_prem => '20000',

 # Add download delay per 100 Mb file, seconds
 add_download_delay_prem => '0',

 # Allow remote URL uploads
 remote_url_prem => '1',

 # Generate direct links
 direct_links_prem => '1',

 # Download speed limit, Kbytes/s
 down_speed_prem => '',

 # Maximum download size in Mbytes (0 to disable) 
 max_download_filesize_prem => '1000',

 max_rs_leech_prem => '1000',

 torrent_dl_prem => '1',

#------#

 # Logfile name
 admin_log => 'logs.txt',

 items_per_page => '20',

 # Files per dir, do not touch since server start
 files_per_folder => 5000,

 # Do not use, for demo site only
 demo_mode => 0,

##### Email settings #####

 # SMTP settings (optional)
 smtp_server   => '',
 smtp_user     => '',
 smtp_pass     => '',

 # This email will be in "From:" field in confirmation & contact emails
 email_from => '',

 # Subject for email notification
 email_subject      => "XFileSharing: new file(s) uploaded",

 # Email that Contact messages will be sent to
 contact_email => '',

 # Premium users payment plans
 # Example: 5.00=7,9.00=14,15.00=30 ($5.00 adds 7 premium days)
 payment_plans => '1.00=7,5.00=14,9.00=30,15.00=120',

 tier_sizes => '0|10|100',

 tier1_countries => 'US|CA',

 tier2_countries => 'DE|FR|GB',

 tier3_countries => 'OTHERS',

 ### Payment settings ###

 item_name => 'FileSharing+Service',
 currency_code => 'USD',

 paypal_email => 'mvpsworld@gmail.com',
 paypal_url    => 'https://www.paypal.com/cgi-bin/webscr',
 #paypal_url	=> 'https://www.sandbox.paypal.com/cgi-bin/webscr',

 alertpay_email => '',

 # User registration coupons
 coupons => 'free1=1',

 tla_xml_key => '',

 webmoney_merchant_id => '',
 webmoney_secret_key => '',

 smscoin_id => '',

 external_links => 'http://sibsoft.net/xfs|XFileSharing engine',

 # Language list to show on site
 languages_list => ['english','russian','german','french','arabic','turkish','polish','thai','spanish','japan','hungary','indonesia'],

 show_server_stats => '1',

### NEW 1.7 ###

 # Start mp3 playing instantly
 mp3_mod_autoplay => '',

 # Match list between browser language code and language file
 # Full list could be found here: http://www.livio.net/main/charset.asp#language
 language_codes => {'en.*'             => 'english',
                    'cs'               => 'czech',
                    'da'               => 'danish',
                    'fr.*'             => 'french',
                    'de.*'             => 'german',
                    'p'                => 'polish',
                    'ru'               => 'russian',
                    'es.*'             => 'spanish',
                   },

 # Cut long filenames in MyFiles,AdminFiles
 display_max_filename => '40',

 # Delete records from IP2Files older than X days
 clean_ip2files_days => '14',

 paypal_subscription => '',

 domain => '',

 daopay_app_id => '',

 m_w => '',

 m_s => '',
 m_s_reg => '',

 anti_dupe_system => '',

 m_i_width => '200',
 m_i_height => '200',
 m_i_resize => '0',
 m_i_wm_position => '',
 m_i_wm_image => '',
 m_i_wm_padding => '',

 two_checkout_sid => '',

 torrent_dl_slots_reg => '',
 torrent_dl_slots_prem => '',

 plimus_contract_id => '',

 moneybookers_email => '',

 cashu_merchant_id => '',

 m_d => '',
 m_d_f => '',
 m_d_a => '',
 m_d_c => '',

 deurl_site => '',
 deurl_api_key => '',

 m_h => '',
 m_h_login => '',
 m_h_password => '',

 m_a => '',

 m_v_width => '400',
 m_v_height => '300',

 video_embed_anon => '',
 video_embed_reg => '1',
 video_embed_prem => '1',

### NEW 1.8 ###

 m_e => '',
 m_e_vid_width => '',
 m_e_vid_quality => '',
 m_e_audio_bitrate => '',

 m_u => '',

 flash_upload_anon => '',
 flash_upload_reg => '1',
 flash_upload_prem => '1',

 files_expire_access_anon => '30',
 files_expire_access_reg => '60',
 files_expire_access_prem => '180',

 # Add download delay after each file download, seconds
 file_dl_delay_anon => '90',
 file_dl_delay_reg => '60',
 file_dl_delay_prem => '0',

 m_n => '',

 max_money_last24 => '100',

 sale_aff_percent => '30',

 referral_aff_percent => '5',

 min_payout => '50',

 del_money_file_del => '',

 convert_money => '3',
 convert_days => '7',

 money_filesize_limit => '',

 dl_money_anon => '',
 dl_money_reg => '',
 dl_money_prem => '',

 tier1_money => '1|2|3',
 tier2_money => '1|2|3',
 tier3_money => '1|2|3',

 rs_logins => '',
 mf_logins => '',
 fs_logins => '',
 df_logins => '',
 ff_logins => '',
 es_logins => '',
 sm_logins => '',
 ug_logins => '',
 fe_logins => '',

 m_i_hotlink_orig => '1',

 payout_systems => 'PayPal, Webmoney, Moneybookers, AlertPay, Plimus',

 mp3_mod_embed => '1',

 mp3_embed_anon => '',
 mp3_embed_reg => '1',
 mp3_embed_prem => '1',

 m_b => '',
 rar_info_anon => '',
 rar_info_reg => '',
 rar_info_prem => '',


 twit_consumer1 => 'Ib9LtBjGpyKhrBKFgnJqag',
 twit_consumer2 => '3n8VdCQjgw4Qi9aMnxlzrm5KCw4Fsv6RlTlcIS5QO4g',
};

1;
