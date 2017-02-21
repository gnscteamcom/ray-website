#!/usr/bin/perl
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib '.';
use XFileConfig;
use Session;
use CGI;
use LWP::UserAgent;
use Data::Dumper;
use Digest::MD5 qw(md5_hex);
#use Digest::SHA1  qw(sha1_hex);
use Digest::SHA::PurePerl qw(sha1_hex);

my $ses = Session->new();
my $f = $ses->f;
my $db= $ses->db;

writeLog( 'Prepared POST data: ' . Dumper($f) );

my $transaction;
if($f->{ap_status} && $f->{apc_1})
{
   &AlertPayChecks;
}
elsif($f->{s_sign_v2})
{
   &SMSCoinChecks;
}
elsif($f->{LMI_PAYEE_PURSE})
{
   &WebmoneyChecks;
}
elsif($f->{appcode} && $f->{origin})
{
   &DaoPayChecks;
}
elsif($f->{cart_order_id})
{
   &TwoCheckoutChecks;
}
elsif($f->{overridePrice} && $f->{custom1})
{
   &PlimusChecks;
}
elsif($f->{mb_transaction_id})
{
   &MoneybookersChecks;
}
elsif($f->{verificationString})
{
   &CashUChecks;
}
else
{
   &PayPalChecks;
}

writeLog( 'Resubmitting detected', 'EXIT' ) if $transaction->{verified} && $transaction->{txn_id} eq $f->{txn_id};

unless($transaction->{usr_id})
{
   $transaction->{login} = join '', map int rand 10, 1..7;
   while($db->SelectOne("SELECT usr_id FROM Users WHERE usr_login=?",$transaction->{login})){ $transaction->{login} = join '', map int rand 10, 1..7; }
   $transaction->{password} = $ses->randchar(10);
   $db->Exec("INSERT INTO Users (usr_login,usr_email,usr_password,usr_created,usr_aff_id) VALUES (?,?,ENCODE(?,?),NOW(),?)",$transaction->{login},$f->{payer_email}||'',$transaction->{password},$c->{pasword_salt},$transaction->{aff_id}||0);
   $transaction->{usr_id} = $db->getLastInsertId;
   $db->Exec("UPDATE Transactions SET usr_id=? WHERE id=?",$transaction->{usr_id},$transaction->{id});
}
else
{
  my $xx = $db->SelectRow("SELECT usr_login, DECODE(usr_password,?) as password FROM Users WHERE usr_id=?",$c->{pasword_salt},$transaction->{usr_id});
  $transaction->{login} = $xx->{usr_login};
  $transaction->{password} = $xx->{password};
}

my $user = $db->SelectRow("SELECT *, UNIX_TIMESTAMP(usr_premium_expire)-UNIX_TIMESTAMP() as exp_sec 
                           FROM Users 
                           WHERE usr_id=?", $transaction->{usr_id} );

$user->{exp_sec}=0 if $user->{exp_sec}<0;
my $plans;
my @arr = split(/,/,$c->{payment_plans});
for(@arr)
{
   /([\d\.]+)=(\d+)/;
   $plans->{sprintf("%.02f",$1)}=$2;
}

    writeLog( "User login: $user->{usr_login}" );
    writeLog( "User expire time is : $user->{usr_premium_expire}" );
    writeLog( "Current time is ".localtime() );
    writeLog( "User data: $transaction->{amount} = ".$plans->{$transaction->{amount}} );
    writeLog( "WARNING: Plan haven't found" ) unless $plans->{$transaction->{amount}};

    $user->{exp_sec} += $plans->{$transaction->{amount}}*24*3600;

    # Add premium days
    $db->Exec("UPDATE Users SET usr_premium_expire=NOW()+INTERVAL ? SECOND WHERE usr_id=?", $user->{exp_sec}, $transaction->{usr_id} );

    if($c->{sale_aff_percent} && $transaction->{aff_id}=~/^\d+$/)
    {
       my $money = $transaction->{amount}*$c->{sale_aff_percent}/100;
       $db->Exec("UPDATE Users 
                  SET usr_money=usr_money+? 
                  WHERE usr_id=?", $money, $transaction->{aff_id});

       $db->Exec("INSERT INTO Stats2
                  SET usr_id=?, day=CURDATE(),
                      sales=1, profit_sales=?
                  ON DUPLICATE KEY UPDATE
                      sales=sales+1, profit_sales=profit_sales+?
                 ",$transaction->{aff_id},$money,$money) if $c->{m_s};

       my $aff_id = $db->SelectOne("SELECT usr_aff_id FROM Users WHERE usr_id=?",$transaction->{aff_id});
       my $money_ref = sprintf("%.05f",$money*$c->{referral_aff_percent}/100);
       if($aff_id && $money_ref>0)
       {
          $db->Exec("UPDATE Users SET usr_money=usr_money+? WHERE usr_id=?", $money_ref, $aff_id);
          $db->Exec("INSERT INTO Stats2
                     SET usr_id=?, day=CURDATE(),
                         profit_refs=?
                     ON DUPLICATE KEY UPDATE
                         profit_refs=profit_refs+?
                    ",$aff_id,$money_ref,$money_ref) if $c->{m_s};
       }
    }
    

    # mark transaction to verified
    $db->Exec("Update Transactions SET verified=1, txn_id=? WHERE id=?", $f->{txn_id}||'', $transaction->{id} );
    writeLog( "Transaction committed" );

    $db->Exec("INSERT INTO Stats SET day=CURDATE(), paid=$transaction->{amount} ON DUPLICATE KEY UPDATE paid=paid+$transaction->{amount}");

    $user = $db->SelectRow("SELECT * FROM Users WHERE usr_id=?", $transaction->{usr_id} );

    # Send email to user
    my $t = $ses->CreateTemplate("payment_notification.html");
    $t->param('amount' => $transaction->{amount},
              'days'   => $plans->{$transaction->{amount}},
              'expire' => $user->{usr_premium_expire},
              'login'  => $transaction->{login},
              'password' => $transaction->{password},
             );
    $c->{email_text}=1;
    $ses->SendMail($user->{usr_email}, $c->{email_from}, "$c->{site_name} Payment Notification", $t->output) if $user->{usr_email};

    # Send email to admin
    my $t = $ses->CreateTemplate("payment_notification_admin.html");
    $t->param('amount' => $transaction->{amount},
              'days'   => $plans->{$transaction->{amount}},
              'expire' => $user->{usr_premium_expire},
              'usr_id' => $user->{usr_id},
              'usr_login' => $user->{usr_login},
             );
    $c->{email_text}=0;
    $ses->SendMail($c->{contact_email}, $c->{email_from}, "Received payment from $user->{usr_login}", $t->output);

writeLog( "Finishing session from '$ENV{REMOTE_ADDR}' - - - - - - - - - - - - - " );
if($f->{cart_order_id} || $f->{verificationString}) #2CO or CashU
{
   my $loginfo="<br><br>Login: $transaction->{login}<br>Password: $transaction->{password}" if $transaction->{password};
   print("Content-type:text/html\n\nPayment complete.<br>Added Premium Days:".$plans->{$transaction->{amount}}.$loginfo."<br><br>Back to main site: <a href='$c->{site_url}'>$c->{site_url}</a>");
   exit;
}
print"Content-type: text/plain\n\n";
writeLog( "Done." );
exit;

#----------------------

sub PayPalChecks
{
    $transaction = $db->SelectRow("SELECT * FROM Transactions WHERE id=?",$f->{custom}) || writeLog( "Transaction not found: '$f->{custom}'", 'EXIT' );

    #$db->Exec("UPDATE Transactions SET txn_id=? WHERE id=?",$f->{txn_id}||'',$transaction->{id});

    writeLog("Wrong mc_amount value: $f->{mc_gross}",'EXIT') 
      unless $f->{mc_gross}==$transaction->{amount};
    writeLog("Wrong mc_currency value: $f->{mc_currency}",'EXIT') 
      unless lc $f->{mc_currency} eq lc $c->{currency_code};
    #writeLog("Wrong receiver_email value: $f->{business}",'EXIT') 
    #  unless lc $f->{business} eq lc $c->{paypal_email};
    writeLog("Wrong txn_id value: $f->{txn_id}",'EXIT') 
      unless $f->{txn_id};

   my $ua = LWP::UserAgent->new(agent => 'application/x-www-form-urlencoded', timeout => 90);
   my $data = [ map {$_=>$f->{$_}} %{$f} ];
   push @$data, 'cmd', '_notify-validate';
   my $res = $ua->post( $c->{paypal_url}, $data );
   writeLog("Got answer: ".$res->content);
   
   writeLog( 'Error HTTP', 'EXIT' ) if $res->is_error;
   writeLog( 'Transaction invalid', 'EXIT' ) unless lc $res->content eq 'verified';
}

#----------------------

sub AlertPayChecks
{
   $transaction = $db->SelectRow("SELECT * FROM Transactions WHERE id=?",$f->{apc_1}) || writeLog( "Transaction not found: '$f->{apc_1}'", 'EXIT' );
   $f->{txn_id} = $f->{ap_referencenumber};
   $f->{payer_email} = $f->{ap_custemailaddress};
   #$db->Exec("UPDATE Transactions SET txn_id=? WHERE id=?",$f->{txn_id}||'',$transaction->{id});
   writeLog("Transaction is not successfull!",'EXIT') unless $f->{ap_status} eq 'Success';
   writeLog("Currency changed!",'EXIT') unless $f->{ap_currency} eq $c->{currency_code};
   writeLog("Amount changed!",'EXIT') unless $f->{ap_totalamount}==$transaction->{amount};
}

#----------------------

sub WebmoneyChecks
{
   $transaction = $db->SelectRow("SELECT * FROM Transactions WHERE id=?",$f->{LMI_PAYMENT_NO}) || writeLog( "Transaction not found: '$f->{LMI_PAYMENT_NO}'", 'EXIT' );
   writeLog("Amount changed!",'EXIT') unless $f->{LMI_PAYMENT_AMOUNT}==$transaction->{amount};
   writeLog("Wrong wallet!",'EXIT') unless $f->{LMI_PAYEE_PURSE}==$c->{webmoney_merchant_id};
   if($f->{LMI_PREREQUEST})
   {
      print"Content-type:text/html\n\nYES";
      exit;
   }
   $f->{txn_id} = $f->{LMI_PAYER_PURSE};
   #$db->Exec("UPDATE Transactions SET txn_id=? WHERE id=?",$f->{txn_id}||'',$transaction->{id});
   
   my $hash_str = $f->{LMI_PAYEE_PURSE}.$f->{LMI_PAYMENT_AMOUNT}.$f->{LMI_PAYMENT_NO}.
                  $f->{LMI_MODE}.$f->{LMI_SYS_INVS_NO}.$f->{LMI_SYS_TRANS_NO}.
                  $f->{LMI_SYS_TRANS_DATE}.$c->{webmoney_secret_key}.$f->{LMI_PAYER_PURSE}.$f->{LMI_PAYER_WM};

   my $hash = uc md5_hex($hash_str);
   print"$hash\n";
   writeLog("MD5 hash invalid!",'EXIT') unless $hash eq $f->{LMI_HASH};
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

sub SMSCoinChecks
{
   $transaction = $db->SelectRow("SELECT * FROM Transactions WHERE id=?",$f->{s_order_id}) || writeLog( "Transaction not found_sms: '$f->{s_order_id}'", 'EXIT' );

   my $reference = ref_sign($c->{dl_key}, $f->{s_purse}, $f->{s_order_id}, $f->{s_amount}, $f->{s_clear_amount}, $f->{s_inv}, $f->{s_phone});
   writeLog("Signature doesn't match!",'EXIT') unless $f->{s_sign_v2} eq $reference;
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

sub DaoPayChecks
{
   my ($id,undef)=split('-',$f->{payment_complete});
   $transaction = $db->SelectRow("SELECT * FROM Transactions WHERE id=?",$id) || writeLog( "Transaction not found_dao: $id''", 'EXIT' );
   writeLog("Amount changed!",'EXIT') unless $transaction->{amount}==$f->{prodprice};
   writeLog("Currency changed!",'EXIT') unless lc($c->{currency_code}) eq lc($f->{prodcurrency});
   writeLog("Not paid full!",'EXIT') unless $f->{'stat'} eq 'ok';
   writeLog("Wrong App ID!",'EXIT') unless $c->{daopay_app_id} == $f->{appcode};
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

sub TwoCheckoutChecks
{
   $transaction = $db->SelectRow("SELECT * FROM Transactions WHERE id=?",$f->{cart_order_id}) || writeLog( "Transaction not found: '$f->{cart_order_id}'", 'EXIT' );
   writeLog("Demo mode!",'EXIT') if $f->{demo};
   writeLog("Transaction is not successfull!",'EXIT') unless $f->{'credit_card_processed'}=~/^(Y|P)$/i;
   writeLog("Amount changed!",'EXIT') unless $f->{total}==$transaction->{amount};
   #writeLog("Security error!",'EXIT') unless $ENV{HTTP_REFERER} =~ m#https?:://([^/]*)(www\.2checkout\.com|2checkout\.com|www2\.2checkout\.com)#i;
   $f->{payer_email} = $f->{email};
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

sub PlimusChecks
{
   my $id = ref($f->{custom1}) eq 'ARRAY' ? $f->{custom1}->[0] : $f->{custom1};
   $transaction = $db->SelectRow("SELECT * FROM Transactions WHERE id=?",$id) || writeLog( "Transaction not found_plimus: $id", 'EXIT' );
   $f->{txn_id}=$f->{referenceNumber};
   $f->{payer_email} = $f->{email};
   writeLog("Amount changed!",'EXIT') unless $f->{overridePrice}==$transaction->{amount};
   writeLog("Currency changed!",'EXIT') unless lc($c->{currency_code}) eq lc($f->{currency});
   writeLog("Declined trnsaction!",'EXIT') if $f->{transactionType} eq 'DECLINE';
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

sub MoneybookersChecks
{
   my $id = $f->{transaction_id};
   $transaction = $db->SelectRow("SELECT * FROM Transactions WHERE id=?",$id) || writeLog( "Transaction not found_plimus: $id", 'EXIT' );
   $f->{txn_id}=$f->{mb_transaction_id};
   $f->{payer_email} = $f->{pay_from_email};
   writeLog("Amount changed!",'EXIT') unless $f->{amount}==$transaction->{amount};
   writeLog("Currency changed!",'EXIT') unless lc($f->{currency}) eq lc($c->{currency_code});
   writeLog("Wrong merchant email!",'EXIT') unless $f->{pay_to_email} eq $c->{moneybookers_email};
   writeLog("Failed status!",'EXIT') unless $f->{status} eq '2';
   
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

sub CashUChecks
{
   $transaction = $db->SelectRow("SELECT * FROM Transactions WHERE id=?",$f->{session_id}) || writeLog( "Transaction not found_cashu: '$f->{session_id}'", 'EXIT' );
   writeLog("Amount changed!",'EXIT') unless $f->{amount}==$transaction->{amount};
   writeLog("Test mode!",'EXIT') if $f->{test_mode};

   my $hex = sha1_hex("$c->{cashu_merchant_id}:$f->{trn_id}:$c->{dl_key}");
   writeLog("Security Hash do not pass",'EXIT') if $f->{verificationString} ne $hex;
}

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

sub ref_sign
{
     local $_ = join("::", @_);
     return md5_hex($_);
}

sub writeLog
{
   my ( $message, $isExit ) = @_;

   if($message)
   {
       open  LOG, ">>ipn_log.txt";
       print LOG localtime()." : $message\n";
       close LOG;
   }

   print("Content-type:text/html\n\n"),exit if $isExit;
   #exit if $isExit;
}

