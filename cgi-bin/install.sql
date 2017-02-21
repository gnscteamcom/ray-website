CREATE TABLE `Comments` (
  `cmt_id` int(10) unsigned NOT NULL auto_increment,
  `usr_id` mediumint(8) unsigned NOT NULL default '0',
  `cmt_type` tinyint(3) unsigned NOT NULL default '0',
  `cmt_ext_id` int(10) unsigned NOT NULL default '0',
  `cmt_ip` int(10) unsigned NOT NULL default '0',
  `cmt_name` varchar(32) NOT NULL default '',
  `cmt_email` varchar(64) NOT NULL default '',
  `cmt_website` varchar(100) NOT NULL default '',
  `cmt_text` text NOT NULL,
  `created` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  PRIMARY KEY  (`cmt_id`),
  KEY `ext` (`cmt_type`,`cmt_ext_id`),
  KEY `date` (`created`),
  KEY `user` (`usr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
CREATE TABLE `DelReasons` (
  `file_code` varchar(12) NOT NULL default '',
  `file_name` varchar(100) NOT NULL default '',
  `info` varchar(255) NOT NULL default '',
  `last_access` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  PRIMARY KEY  (`file_code`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
CREATE TABLE `Files` (
  `file_id` int(10) unsigned NOT NULL auto_increment,
  `usr_id` mediumint(8) unsigned NOT NULL default '0',
  `srv_id` smallint(5) unsigned NOT NULL default '0',
  `file_name` varchar(255) NOT NULL default '',
  `file_descr` varchar(255) NOT NULL default '',
  `file_public` tinyint(3) unsigned NOT NULL default '0',
  `file_code` varchar(12) NOT NULL default '',
  `file_real` varchar(12) NOT NULL default '',
  `file_real_id` int(10) unsigned NOT NULL default '0',
  `file_del_id` varchar(10) NOT NULL default '',
  `file_fld_id` int(11) NOT NULL default '0',
  `file_downloads` int(10) unsigned NOT NULL default '0',
  `file_size` bigint(20) unsigned NOT NULL default '0',
  `file_password` varchar(32) NOT NULL default '',
  `file_ip` int(20) unsigned NOT NULL default '0',
  `file_md5` varchar(64) NOT NULL default '',
  `file_spec` text NOT NULL,
  `file_last_download` datetime NOT NULL default '0000-00-00 00:00:00',
  `file_created` datetime NOT NULL default '0000-00-00 00:00:00',
  `file_money` decimal(10,4) unsigned NOT NULL default '0.0000',
  `file_ipb_topic_id` int(10) unsigned NOT NULL default '0',
  PRIMARY KEY  (`file_id`),
  KEY `real` (`file_real`),
  KEY `server` (`srv_id`),
  KEY `created` (`file_created`),
  KEY `code` (`file_code`),
  KEY `public` (`file_public`),
  KEY `user` (`usr_id`),
  KEY `folder` (`file_fld_id`),
  KEY `size` (`file_size`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
CREATE TABLE `Folders` (
  `fld_id` int(10) unsigned NOT NULL auto_increment,
  `usr_id` mediumint(8) unsigned NOT NULL default '0',
  `fld_parent_id` int(10) unsigned NOT NULL default '0',
  `fld_descr` text NOT NULL,
  `fld_name` varchar(128) NOT NULL default '',
  PRIMARY KEY  (`fld_id`),
  KEY `user` (`usr_id`,`fld_parent_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
CREATE TABLE `IP2Files` (
  `file_id` int(10) unsigned NOT NULL default '0',
  `ip` int(20) unsigned NOT NULL default '0',
  `usr_id` mediumint(8) unsigned NOT NULL default '0',
  `owner_id` mediumint(8) unsigned NOT NULL default '0',
  `size` bigint(20) unsigned NOT NULL default '0',
  `money` decimal(8,4) unsigned NOT NULL default '0.0000',
  `referer` varchar(255) NOT NULL default '',
  `created` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  PRIMARY KEY  (`file_id`,`ip`,`usr_id`),
  KEY `owner` (`owner_id`),
  KEY `user` (`usr_id`),
  KEY `ip` (`ip`,`created`),
  KEY `date` (`created`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
CREATE TABLE `IP2RS` (
  `created` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `usr_id` mediumint(8) unsigned NOT NULL default '0',
  `size` bigint(20) unsigned NOT NULL default '0',
  `ip` int(10) unsigned NOT NULL default '0',
  KEY `created` (`created`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
CREATE TABLE `News` (
  `news_id` mediumint(9) unsigned NOT NULL auto_increment,
  `news_title` varchar(100) NOT NULL default '',
  `news_title2` varchar(100) NOT NULL default '',
  `news_text` text NOT NULL,
  `created` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`news_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
CREATE TABLE `Payments` (
  `id` mediumint(8) unsigned NOT NULL auto_increment,
  `usr_id` mediumint(8) unsigned NOT NULL default '0',
  `amount` decimal(7,2) unsigned NOT NULL default '0.00',
  `status` enum('PENDING','PAID','REJECTED') NOT NULL default 'PENDING',
  `created` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`id`),
  KEY `user` (`usr_id`),
  KEY `stat` (`status`,`created`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
CREATE TABLE `Reports` (
  `id` int(10) unsigned NOT NULL auto_increment,
  `file_id` int(10) unsigned NOT NULL default '0',
  `usr_id` mediumint(8) unsigned default '0',
  `filename` varchar(100) NOT NULL default '',
  `name` varchar(64) NOT NULL default '',
  `email` varchar(64) NOT NULL default '',
  `reason` varchar(100) NOT NULL default '',
  `info` text NOT NULL,
  `ip` int(20) unsigned NOT NULL default '0',
  `status` enum('PENDING','APPROVED','DECLINED') NOT NULL default 'PENDING',
  `ban_size` bigint(20) unsigned default '0',
  `ban_md5` varchar(64) default '',
  `created` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`id`),
  KEY `status` (`status`),
  KEY `ban` (`ban_size`,`ban_md5`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
CREATE TABLE `Servers` (
  `srv_id` smallint(5) unsigned NOT NULL auto_increment,
  `srv_name` varchar(64) NOT NULL default '',
  `srv_ip` varchar(16) NOT NULL default '',
  `srv_cgi_url` varchar(255) NOT NULL default '',
  `srv_htdocs_url` varchar(255) NOT NULL default '',
  `srv_key` varchar(8) NOT NULL default '',
  `srv_disk_max` bigint(20) unsigned NOT NULL default '0',
  `srv_status` enum('ON','READONLY','OFF') NOT NULL default 'ON',
  `srv_files` int(10) unsigned NOT NULL default '0',
  `srv_disk` bigint(20) unsigned NOT NULL default '0',
  `srv_allow_regular` tinyint(1) unsigned NOT NULL default '0',
  `srv_allow_premium` tinyint(1) unsigned NOT NULL default '0',
  `srv_torrent` tinyint(3) unsigned NOT NULL default '0',
  `srv_created` date NOT NULL default '0000-00-00',
  `srv_last_upload` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`srv_id`),
  UNIQUE KEY `fs_key` (`srv_key`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
CREATE TABLE `Sessions` (
  `session_id` char(16) NOT NULL default '',
  `usr_id` mediumint(8) unsigned NOT NULL default '0',
  `last_time` datetime NOT NULL default '0000-00-00 00:00:00',
  PRIMARY KEY  (`session_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
CREATE TABLE `Stats` (
  `day` date NOT NULL default '0000-00-00',
  `uploads` mediumint(8) unsigned NOT NULL default '0',
  `downloads` mediumint(8) unsigned NOT NULL default '0',
  `registered` smallint(5) unsigned NOT NULL default '0',
  `bandwidth` bigint(20) unsigned NOT NULL default '0',
  `paid` decimal(7,2) NOT NULL default '0.00',
  PRIMARY KEY  (`day`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
CREATE TABLE `Stats2` (
  `usr_id` mediumint(8) unsigned NOT NULL default '0',
  `day` date NOT NULL default '0000-00-00',
  `downloads` int(10) unsigned NOT NULL default '0',
  `sales` smallint(5) unsigned NOT NULL default '0',
  `profit_dl` decimal(9,4) unsigned NOT NULL default '0.0000',
  `profit_sales` decimal(9,4) unsigned NOT NULL default '0.0000',
  `profit_refs` decimal(9,5) unsigned NOT NULL default '0.00000',
  PRIMARY KEY  (`usr_id`,`day`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
CREATE TABLE `Torrents` (
  `sid` varchar(100) NOT NULL default '',
  `usr_id` mediumint(8) unsigned NOT NULL default '0',
  `srv_id` smallint(5) unsigned NOT NULL default '0',
  `files` text NOT NULL,
  `progress` varchar(100) NOT NULL default '',
  `status` enum('WORKING','DONE') NOT NULL default 'WORKING',
  `created` datetime NOT NULL default '0000-00-00 00:00:00',
  KEY `sid` (`sid`),
  KEY `user` (`usr_id`),
  KEY `status` (`status`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
CREATE TABLE `Transactions` (
  `id` varchar(10) NOT NULL default '',
  `usr_id` mediumint(9) unsigned NOT NULL default '0',
  `amount` decimal(10,2) unsigned NOT NULL default '0.00',
  `txn_id` varchar(100) NOT NULL default '',
  `created` datetime NOT NULL default '0000-00-00 00:00:00',
  `aff_id` mediumint(8) unsigned NOT NULL default '0',
  `ip` int(20) unsigned NOT NULL default '0',
  `verified` tinyint(4) unsigned NOT NULL default '0',
  PRIMARY KEY  (`id`),
  KEY `user` (`usr_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
CREATE TABLE `UserData` (
  `usr_id` mediumint(8) unsigned NOT NULL auto_increment,
  `name` varchar(24) NOT NULL default '',
  `value` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`usr_id`,`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
CREATE TABLE `Users` (
  `usr_id` mediumint(8) unsigned NOT NULL auto_increment,
  `usr_login` varchar(32) NOT NULL default '',
  `usr_password` varchar(100) NOT NULL default '',
  `usr_email` varchar(64) NOT NULL default '',
  `usr_adm` tinyint(3) unsigned NOT NULL default '0',
  `usr_mod` tinyint(3) unsigned NOT NULL default '0',
  `usr_status` enum('OK','PENDING','BANNED') NOT NULL default 'OK',
  `usr_premium_expire` datetime NOT NULL default '0000-00-00 00:00:00',
  `usr_direct_downloads` tinyint(1) unsigned NOT NULL default '0',
  `usr_rapid_login` varchar(32) NOT NULL default '',
  `usr_rapid_pass` varchar(32) NOT NULL default '',
  `usr_aff_id` mediumint(8) unsigned NOT NULL default '0',
  `usr_created` datetime NOT NULL default '0000-00-00 00:00:00',
  `usr_lastlogin` datetime NOT NULL default '0000-00-00 00:00:00',
  `usr_lastip` int(20) unsigned NOT NULL default '0',
  `usr_pay_email` varchar(64) NOT NULL default '',
  `usr_pay_type` varchar(16) NOT NULL default '',
  `usr_disk_space` mediumint(8) unsigned NOT NULL default '0',
  `usr_money` decimal(11,5) unsigned NOT NULL default '0.00000',
  PRIMARY KEY  (`usr_id`),
  KEY `login` (`usr_login`),
  KEY `aff_id` (`usr_aff_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;