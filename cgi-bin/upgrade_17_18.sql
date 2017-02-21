ALTER TABLE Files
    ADD file_money decimal(10,4) unsigned NOT NULL DEFAULT '0.0000' COMMENT '' AFTER file_created,
    MODIFY usr_id mediumint(8) unsigned NOT NULL DEFAULT '0' COMMENT '',
    MODIFY file_descr varchar(255) NOT NULL DEFAULT '' COMMENT '' COLLATE utf8_general_ci,
    MODIFY file_password varchar(32) NOT NULL DEFAULT '' COMMENT '' COLLATE utf8_general_ci,
    MODIFY file_ip int(20) unsigned NOT NULL DEFAULT '0' COMMENT '';
ALTER TABLE IP2Files
    ADD money decimal(8,4) unsigned NOT NULL DEFAULT '0.0000' COMMENT '' AFTER size,
    DROP points;
ALTER TABLE IP2RS
    ADD size bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT '' AFTER usr_id;
ALTER TABLE Stats2
    ADD sales smallint(5) unsigned NOT NULL DEFAULT '0' COMMENT '' AFTER downloads,
    MODIFY profit_dl decimal(9,4) unsigned NOT NULL DEFAULT '0.0000' COMMENT '',
    MODIFY profit_sales decimal(9,4) unsigned NOT NULL DEFAULT '0.0000' COMMENT '',
    MODIFY profit_refs decimal(9,5) unsigned NOT NULL DEFAULT '0.00000' COMMENT '';