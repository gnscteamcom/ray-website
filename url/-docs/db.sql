-- Create syntax for TABLE 'settings'
CREATE TABLE `settings` (
  `location` text NOT NULL,
  `bar` int(11) NOT NULL,
  `analytics` text NOT NULL,
  `ads` int(11) NOT NULL,
  `socialmedia` int(11) NOT NULL,
  `bookmarklet` int(11) NOT NULL,
  `api` int(11) NOT NULL,
  `name` text NOT NULL,
  `length` int(11) NOT NULL,
  `ad_html` text,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `safe` text,
  `chars` text NOT NULL,
  `splash` int(11) NOT NULL,
  `validurl` int(11) NOT NULL,
  `parabox` text,
  `boxcreate` int(11) NOT NULL,
  `boxvisit` int(11) NOT NULL,
  `pods` int(11) NOT NULL,
  `qr` text NOT NULL,
  `login` text NOT NULL,
  `top3` int(11) NOT NULL,
  `description` int(11) NOT NULL,
  `recentview` int(11) NOT NULL,
  `recentcreate` int(11) NOT NULL,
  KEY `Id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'stats'
CREATE TABLE `stats` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `urlid` int(11) DEFAULT NULL,
  `ip` varchar(200) DEFAULT NULL,
  `locfrom` varchar(200) DEFAULT NULL,
  `country` varchar(200) DEFAULT NULL,
  `language` varchar(200) DEFAULT NULL,
  `time` time DEFAULT NULL,
  `cdate` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=206995 DEFAULT CHARSET=utf8;

-- Create syntax for TABLE 'urls'
CREATE TABLE `urls` (
  `id` bigint(24) NOT NULL AUTO_INCREMENT,
  `short_url` varchar(62) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `url` text CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `created` date NOT NULL DEFAULT '0000-00-00',
  `time` time NOT NULL DEFAULT '00:00:00',
  `hits` int(11) NOT NULL DEFAULT '0',
  `custom` enum('Y','N') CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT 'N',
  PRIMARY KEY (`id`),
  UNIQUE KEY `short_url` (`short_url`),
  KEY `created` (`created`),
  KEY `time` (`time`),
  KEY `hits` (`hits`),
  KEY `custom` (`custom`),
  KEY `url` (`url`(333))
) ENGINE=MyISAM AUTO_INCREMENT=177087 DEFAULT CHARSET=latin1;