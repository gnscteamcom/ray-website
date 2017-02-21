package Net::Twitter::Lite;
use 5.005;
use warnings;
use strict;

our $VERSION = '0.08006';
$VERSION = eval { $VERSION };

use Carp;
use URI::Escape;
use JSON::Any qw/XS JSON/;
use HTTP::Request::Common;
use Net::Twitter::Lite::Error;
use Encode qw/encode_utf8/;

my $json_handler = JSON::Any->new(utf8 => 1);

sub new {
    my ($class, %args) = @_;

    my $ssl   = delete $args{ssl};
    if ( $ssl ) {
        eval { require Crypt::SSLeay } && $Crypt::SSLeay::VERSION >= 0.5
            || croak "Crypt::SSLeay version 0.50 is required for SSL support";
    }

    my $netrc = delete $args{netrc};
    my $new = bless {
        apiurl     => 'http://api.twitter.com/1',
        apirealm   => 'Twitter API',
        $args{identica} ? ( apiurl => 'http://identi.ca/api' ) : (),
        searchurl  => 'http://search.twitter.com',
        useragent  => __PACKAGE__ . "/$VERSION (Perl)",
        clientname => __PACKAGE__,
        clientver  => $VERSION,
        clienturl  => 'http://search.cpan.org/dist/Net-Twitter-Lite/',
        source     => 'twitterpm',
        useragent_class => 'LWP::UserAgent',
        useragent_args  => {},
        oauth_urls => {
            request_token_url  => "http://twitter.com/oauth/request_token",
            authentication_url => "http://twitter.com/oauth/authenticate",
            authorization_url  => "http://twitter.com/oauth/authorize",
            access_token_url   => "http://twitter.com/oauth/access_token",
        },
        netrc_machine => 'api.twitter.com',
        %args
    }, $class;

    $new->{apiurl} =~ s/http/https/ if $ssl;

    # get username and password from .netrc
    if ( $netrc ) {
        eval { require Net::Netrc; 1 }
            || croak "Net::Netrc is required for the netrc option";

        my $host = $netrc eq '1' ? $new->{netrc_machine} : $netrc;
        my $nrc = Net::Netrc->lookup($host)
            || croak "No .netrc entry for $host";

        @{$new}{qw/username password/} = $nrc->lpa;
    }

    $new->{ua} ||= do {
        eval "use $new->{useragent_class}";
        croak $@ if $@;

        $new->{useragent_class}->new(%{$new->{useragent_args}});
    };

    $new->{ua}->agent($new->{useragent});
    $new->{ua}->default_header('X-Twitter-Client'         => $new->{clientname});
    $new->{ua}->default_header('X-Twitter-Client-Version' => $new->{clientver});
    $new->{ua}->default_header('X-Twitter-Client-URL'     => $new->{clienturl});
    $new->{ua}->env_proxy;

    $new->{_authenticator} = exists $new->{consumer_key}
                           ? '_oauth_authenticated_request'
                           : '_basic_authenticated_request';

    $new->credentials(@{$new}{qw/username password/})
        if exists $new->{username} && exists $new->{password};

    return $new;
}

sub credentials {
    my $self = shift;
    my ($username, $password) = @_;

    croak "exected a username and password" unless @_ == 2;
    croak "OAuth authentication is in use"  if exists $self->{consumer_key};

    $self->{username} = $username;
    $self->{password} = $password;

    my $uri = URI->new($self->{apiurl});
    my $netloc = join ':', $uri->host, $uri->port;

    $self->{ua}->credentials($netloc, $self->{apirealm}, $username, $password);
}

sub _oauth {
    my $self = shift;

    return $self->{_oauth} ||= do {
        eval "use Net::OAuth 0.16";
        croak "Install Net::OAuth 0.16 or later for OAuth support" if $@;

        eval '$Net::OAuth::PROTOCOL_VERSION = Net::OAuth::PROTOCOL_VERSION_1_0A';
        die $@ if $@;
        
        'Net::OAuth';
    };
}

# simple check to see if we have access tokens; does not check to see if they are valid
sub authorized {
    my $self = shift;

    return defined $self->{access_token} && $self->{access_token_secret};
}

# OAuth token accessors
for my $method ( qw/
            access_token
            access_token_secret
            request_token
            request_token_secret
        / ) {
    no strict 'refs';
    *{__PACKAGE__ . "::$method"} = sub {
        my $self = shift;
        
        $self->{$method} = shift if @_;
        return $self->{$method};
    };
}

# OAuth url accessors
for my $method ( qw/
            request_token_url
            authentication_url
            authorization_url
            access_token_url
        / ) {
    no strict 'refs';
    *{__PACKAGE__ . "::$method"} = sub {
        my $self = shift;

        $self->{oauth_urls}{$method} = shift if @_;
        return URI->new($self->{oauth_urls}{$method});
    };
}

# get the athorization or authentication url
sub _get_auth_url {
    my ($self, $which_url, %params ) = @_;

    $self->_request_request_token(%params);

    my $uri = $self->$which_url;
    $uri->query_form(oauth_token => $self->request_token);
    return $uri;
}

# get the authentication URL from Twitter
sub get_authentication_url { return shift->_get_auth_url(authentication_url => @_) }

# get the authorization URL from Twitter
sub get_authorization_url { return shift->_get_auth_url(authorization_url => @_) }

# common portion of all oauth requests
sub _make_oauth_request {
    my ($self, $type, %params) = @_;

    my $request = $self->_oauth->request($type)->new(
        version          => '1.0',
        consumer_key     => $self->{consumer_key},
        consumer_secret  => $self->{consumer_secret},
        request_method   => 'GET',
        signature_method => 'HMAC-SHA1',
        timestamp        => time,
        nonce            => time ^ $$ ^ int(rand 2**32),
        %params,
    );

    $request->sign;

    return $request;
}

# called by get_authorization_url to obtain request tokens
sub _request_request_token {
    my ($self, %params) = @_;

    my $uri = $self->request_token_url;
    $params{callback} ||= 'oob';
    my $request = $self->_make_oauth_request(
        'request token',
        request_url => $uri,
        %params,
    );

    my $res = $self->{ua}->get($request->to_url);
    die "GET $uri failed: ".$res->status_line
        unless $res->is_success;

    # reuse $uri to extract parameters from the response content
    $uri->query($res->content);
    my %res_param = $uri->query_form;

    $self->request_token($res_param{oauth_token});
    $self->request_token_secret($res_param{oauth_token_secret});
}

# exchange request tokens for access tokens; call with (verifier => $verifier)
sub request_access_token {
    my ($self, %params ) = @_;

    my $uri = $self->access_token_url;
    my $request = $self->_make_oauth_request(
        'access token',
        request_url => $uri,
        token       => $self->request_token,
        token_secret => $self->request_token_secret,
        %params, # verifier => $verifier
    );

    my $res = $self->{ua}->get($request->to_url);
    die "GET $uri failed: ".$res->status_line
        unless $res->is_success;

    # discard request tokens, they're no longer valid
    delete $self->{request_token};
    delete $self->{request_token_secret};

    # reuse $uri to extract parameters from content
    $uri->query($res->content);
    my %res_param = $uri->query_form;

    return (
        $self->access_token($res_param{oauth_token}),
        $self->access_token_secret($res_param{oauth_token_secret}),
        $res_param{user_id},
        $res_param{screen_name},
    );
}

# common call for both Basic Auth and OAuth
sub _authenticated_request {
    my $self = shift;

    my $authenticator = $self->{_authenticator};
    $self->$authenticator(@_);
}

sub _encode_args {
    my $args = shift;

    return { map { ref($_) ? $_ : encode_utf8 $_ } %$args };
}

sub _oauth_authenticated_request {
    my ($self, $http_method, $uri, $args, $authenticate) = @_;
    
    delete $args->{source}; # not necessary with OAuth requests

    my $is_multipart = grep { ref } %$args;

    my $msg;
    if ( $authenticate && $self->authorized ) {
        local $Net::OAuth::SKIP_UTF8_DOUBLE_ENCODE_CHECK = 1;

        my $request = $self->_make_oauth_request(
            'protected resource',
            request_url    => $uri,
            request_method => $http_method,
            token          => $self->access_token,
            token_secret   => $self->access_token_secret,
            extra_params   => $is_multipart ? {} : $args,
        );

        if ( $http_method eq 'GET' ) {
            $msg = GET($request->to_url);
        }
        elsif ( $http_method eq 'POST' ) {
            $msg = $is_multipart
                 ? POST($request->request_url,
                        Authorization => $request->to_authorization_header,
                        Content_Type  => 'form-data',
                        Content       => [ %$args ],
                   )
                 : POST($$uri, Content => $request->to_post_body)
                 ;
        }
        else {
            croak "unexpected http_method: $http_method";
        }
    }
    elsif ( $http_method eq 'GET' ) {
        $uri->query_form($args);
        $args = {};
        $msg = GET($uri);
    }
    elsif ( $http_method eq 'POST' ) {
        my $encoded_args = { %$args };
        _encode_args($encoded_args);
        $msg = $self->_mk_post_msg($uri, $args);
    }
    else {
        croak "unexpected http_method: $http_method";
    }

    return $self->{ua}->request($msg);
}

sub _basic_authenticated_request {
    my ($self, $http_method, $uri, $args, $authenticate) = @_;

    _encode_args($args);

    my $msg;
    if ( $http_method eq 'GET' ) {
        $uri->query_form($args);
        $msg = GET($uri);
    }
    elsif ( $http_method eq 'POST' ) {
        $msg = $self->_mk_post_msg($uri, $args);
    }

    if ( $authenticate && $self->{username} && $self->{password} ) {
        $msg->headers->authorization_basic(@{$self}{qw/username password/});
    }

    return $self->{ua}->request($msg);
}

sub _mk_post_msg {
    my ($self, $uri, $args) = @_;

    # if any of the arguments are (array) refs, use form-data
    return (grep { ref } values %$args)
         ? POST($uri, Content_Type => 'form-data', Content => [ %$args ])
         : POST($uri, $args);
}

my $api_def = [
    [ REST => [
        [ 'block_exists', {
            aliases     => [ qw// ],
            path        => 'blocks/exists/id',
            method      => 'GET',
            params      => [ qw/id user_id screen_name/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'blocking', {
            aliases     => [ qw// ],
            path        => 'blocks/blocking',
            method      => 'GET',
            params      => [ qw/page/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'blocking_ids', {
            aliases     => [ qw// ],
            path        => 'blocks/blocking/ids',
            method      => 'GET',
            params      => [ qw// ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'create_block', {
            aliases     => [ qw// ],
            path        => 'blocks/create/id',
            method      => 'POST',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'create_favorite', {
            aliases     => [ qw// ],
            path        => 'favorites/create/id',
            method      => 'POST',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'create_friend', {
            aliases     => [ qw/follow_new/ ],
            path        => 'friendships/create/id',
            method      => 'POST',
            params      => [ qw/id user_id screen_name follow/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'create_saved_search', {
            aliases     => [ qw// ],
            path        => 'saved_searches/create',
            method      => 'POST',
            params      => [ qw/query/ ],
            required    => [ qw/query/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'destroy_block', {
            aliases     => [ qw// ],
            path        => 'blocks/destroy/id',
            method      => 'POST',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'destroy_direct_message', {
            aliases     => [ qw// ],
            path        => 'direct_messages/destroy/id',
            method      => 'POST',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'destroy_favorite', {
            aliases     => [ qw// ],
            path        => 'favorites/destroy/id',
            method      => 'POST',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'destroy_friend', {
            aliases     => [ qw/unfollow/ ],
            path        => 'friendships/destroy/id',
            method      => 'POST',
            params      => [ qw/id user_id screen_name/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'destroy_saved_search', {
            aliases     => [ qw// ],
            path        => 'saved_searches/destroy/id',
            method      => 'POST',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'destroy_status', {
            aliases     => [ qw// ],
            path        => 'statuses/destroy/id',
            method      => 'POST',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'direct_messages', {
            aliases     => [ qw// ],
            path        => 'direct_messages',
            method      => 'GET',
            params      => [ qw/since_id max_id count page/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'disable_notifications', {
            aliases     => [ qw// ],
            path        => 'notifications/leave/id',
            method      => 'POST',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'downtime_schedule', {
            aliases     => [ qw// ],
            path        => 'help/downtime_schedule',
            method      => 'GET',
            params      => [ qw// ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 1,
            authenticate => 1,
        } ],
        [ 'enable_notifications', {
            aliases     => [ qw// ],
            path        => 'notifications/follow/id',
            method      => 'POST',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'end_session', {
            aliases     => [ qw// ],
            path        => 'account/end_session',
            method      => 'POST',
            params      => [ qw// ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'favorites', {
            aliases     => [ qw// ],
            path        => 'favorites/id',
            method      => 'GET',
            params      => [ qw/id page/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'followers', {
            aliases     => [ qw// ],
            path        => 'statuses/followers/id',
            method      => 'GET',
            params      => [ qw/id user_id screen_name cursor/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'followers_ids', {
            aliases     => [ qw// ],
            path        => 'followers/ids/id',
            method      => 'GET',
            params      => [ qw/id user_id screen_name cursor/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'friends', {
            aliases     => [ qw/following/ ],
            path        => 'statuses/friends/id',
            method      => 'GET',
            params      => [ qw/id user_id screen_name cursor/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'friends_ids', {
            aliases     => [ qw/following_ids/ ],
            path        => 'friends/ids/id',
            method      => 'GET',
            params      => [ qw/id user_id screen_name cursor/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'friends_timeline', {
            aliases     => [ qw/following_timeline/ ],
            path        => 'statuses/friends_timeline',
            method      => 'GET',
            params      => [ qw/since_id max_id count page/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'friendship_exists', {
            aliases     => [ qw/relationship_exists follows/ ],
            path        => 'friendships/exists',
            method      => 'GET',
            params      => [ qw/user_a user_b/ ],
            required    => [ qw/user_a user_b/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'home_timeline', {
            aliases     => [ qw// ],
            path        => 'statuses/home_timeline',
            method      => 'GET',
            params      => [ qw/since_id max_id count page/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'mentions', {
            aliases     => [ qw/replies/ ],
            path        => 'statuses/replies',
            method      => 'GET',
            params      => [ qw/since_id max_id count page/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'new_direct_message', {
            aliases     => [ qw// ],
            path        => 'direct_messages/new',
            method      => 'POST',
            params      => [ qw/user text screen_name user_id/ ],
            required    => [ qw/user text/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'public_timeline', {
            aliases     => [ qw// ],
            path        => 'statuses/public_timeline',
            method      => 'GET',
            params      => [ qw// ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'rate_limit_status', {
            aliases     => [ qw// ],
            path        => 'account/rate_limit_status',
            method      => 'GET',
            params      => [ qw// ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'report_spam', {
            aliases     => [ qw// ],
            path        => 'report_spam',
            method      => 'POST',
            params      => [ qw/id user_id screen_name/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'retweet', {
            aliases     => [ qw// ],
            path        => 'statuses/retweet/id',
            method      => 'POST',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'retweeted_by_me', {
            aliases     => [ qw// ],
            path        => 'statuses/retweeted_by_me',
            method      => 'GET',
            params      => [ qw/since_id max_id count page/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'retweeted_of_me', {
            aliases     => [ qw// ],
            path        => 'statuses/retweeted_of_me',
            method      => 'GET',
            params      => [ qw/since_id max_id count page/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'retweeted_to_me', {
            aliases     => [ qw// ],
            path        => 'statuses/retweeted_to_me',
            method      => 'GET',
            params      => [ qw/since_id max_id count page/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'retweets', {
            aliases     => [ qw// ],
            path        => 'statuses/retweets/id',
            method      => 'GET',
            params      => [ qw/id count/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'saved_searches', {
            aliases     => [ qw// ],
            path        => 'saved_searches',
            method      => 'GET',
            params      => [ qw// ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'sent_direct_messages', {
            aliases     => [ qw// ],
            path        => 'direct_messages/sent',
            method      => 'GET',
            params      => [ qw/since_id max_id page/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'show_friendship', {
            aliases     => [ qw/show_relationship/ ],
            path        => 'friendships/show',
            method      => 'GET',
            params      => [ qw/source_id source_screen_name target_id target_id_name/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'show_saved_search', {
            aliases     => [ qw// ],
            path        => 'saved_searches/show/id',
            method      => 'GET',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'show_status', {
            aliases     => [ qw// ],
            path        => 'statuses/show/id',
            method      => 'GET',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'show_user', {
            aliases     => [ qw// ],
            path        => 'users/show/id',
            method      => 'GET',
            params      => [ qw/id/ ],
            required    => [ qw/id/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'test', {
            aliases     => [ qw// ],
            path        => 'help/test',
            method      => 'GET',
            params      => [ qw// ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'trends_available', {
            aliases     => [ qw// ],
            path        => 'trends/available',
            method      => 'GET',
            params      => [ qw/lat long/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'trends_location', {
            aliases     => [ qw// ],
            path        => 'trends/location',
            method      => 'GET',
            params      => [ qw/woeid/ ],
            required    => [ qw/woeid/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'update', {
            aliases     => [ qw// ],
            path        => 'statuses/update',
            method      => 'POST',
            params      => [ qw/status lat long in_reply_to_status_id/ ],
            required    => [ qw/status/ ],
            add_source  => 1,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'update_delivery_device', {
            aliases     => [ qw// ],
            path        => 'account/update_delivery_device',
            method      => 'POST',
            params      => [ qw/device/ ],
            required    => [ qw/device/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'update_location', {
            aliases     => [ qw// ],
            path        => 'account/update_location',
            method      => 'POST',
            params      => [ qw/location/ ],
            required    => [ qw/location/ ],
            add_source  => 0,
            deprecated  => 1,
            authenticate => 1,
        } ],
        [ 'update_profile', {
            aliases     => [ qw// ],
            path        => 'account/update_profile',
            method      => 'POST',
            params      => [ qw/name email url location description/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'update_profile_background_image', {
            aliases     => [ qw// ],
            path        => 'account/update_profile_background_image',
            method      => 'POST',
            params      => [ qw/image/ ],
            required    => [ qw/image/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'update_profile_colors', {
            aliases     => [ qw// ],
            path        => 'account/update_profile_colors',
            method      => 'POST',
            params      => [ qw/profile_background_color profile_text_color profile_link_color profile_sidebar_fill_color profile_sidebar_border_color/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'update_profile_image', {
            aliases     => [ qw// ],
            path        => 'account/update_profile_image',
            method      => 'POST',
            params      => [ qw/image/ ],
            required    => [ qw/image/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'user_timeline', {
            aliases     => [ qw// ],
            path        => 'statuses/user_timeline/id',
            method      => 'GET',
            params      => [ qw/id user_id screen_name since_id max_id count page/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'users_search', {
            aliases     => [ qw/find_people search_users/ ],
            path        => 'users/search',
            method      => 'GET',
            params      => [ qw/q per_page page/ ],
            required    => [ qw/q/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
        [ 'verify_credentials', {
            aliases     => [ qw// ],
            path        => 'account/verify_credentials',
            method      => 'GET',
            params      => [ qw// ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 1,
        } ],
    ] ],
    [ Search => [
        [ 'search', {
            aliases     => [ qw// ],
            path        => 'search',
            method      => 'GET',
            params      => [ qw/q callback lang rpp page since_id geocode show_user/ ],
            required    => [ qw/q/ ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 0,
        } ],
        [ 'trends', {
            aliases     => [ qw// ],
            path        => 'trends',
            method      => 'GET',
            params      => [ qw// ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 0,
        } ],
        [ 'trends_current', {
            aliases     => [ qw// ],
            path        => 'trends/current',
            method      => 'GET',
            params      => [ qw/exclude/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 0,
        } ],
        [ 'trends_daily', {
            aliases     => [ qw// ],
            path        => 'trends/daily',
            method      => 'GET',
            params      => [ qw/date exclude/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 0,
        } ],
        [ 'trends_weekly', {
            aliases     => [ qw// ],
            path        => 'trends/weekly',
            method      => 'GET',
            params      => [ qw/date exclude/ ],
            required    => [ qw// ],
            add_source  => 0,
            deprecated  => 0,
            authenticate => 0,
        } ],
    ] ],
];

my $with_url_arg = sub {
    my ($path, $args) = @_;

    if ( defined(my $id = delete $args->{id}) ) {
        $path .= uri_escape($id);
    }
    else {
        chop($path);
    }
    return $path;
};

while ( @$api_def ) {
    my $api = shift @$api_def;
    my $api_name = shift @$api;
    my $methods = shift @$api;

    my $url_attr = $api_name eq 'REST' ? 'apiurl' : 'searchurl';

    my $base_url = sub { shift->{$url_attr} };

    for my $method ( @$methods ) {
        my $name    = shift @$method;
        my %options = %{ shift @$method };

        my ($arg_names, $path) = @options{qw/required path/};
        $arg_names = $options{params} if @$arg_names == 0 && @{$options{params}} == 1;

        my $modify_path = $path =~ s,/id$,/, ? $with_url_arg : sub { $_[0] };

        my $code = sub {
            my $self = shift;

            # copy callers args since we may add ->{source}
            my $args = ref $_[-1] eq 'HASH' ? { %{pop @_} } : {};

            if ( @_ ) {
                @_ == @$arg_names || croak "$name expected @{[ scalar @$arg_names ]} args";
                @{$args}{@$arg_names} = @_;
            }
            $args->{source} ||= $self->{source} if $options{add_source};

            my $authenticate = exists $args->{authenticate}  ? delete $args->{authenticate}
                             : $options{authenticate}
                             ;

            my $local_path = $modify_path->($path, $args);
            
            my $uri = URI->new($base_url->($self) . "/$local_path.json");

            return $self->_parse_result(
                $self->_authenticated_request($options{method}, $uri, $args, $authenticate)
            );
        };

        no strict 'refs';
        *{__PACKAGE__ . "::$_"} = $code for $name, @{$options{aliases}};
    }
}

sub _from_json {
    my ($self, $json) = @_;

    return eval { $json_handler->from_json($json) };
}

sub _parse_result {
    my ($self, $res) = @_;

    my $content = $res->content;
    $content =~ s/^"(true|false)"$/$1/;

    my $obj = $self->_from_json($content);

    # Twitter sometimes returns an error with status code 200
    if ( $obj && ref $obj eq 'HASH' && exists $obj->{error} ) {
        die Net::Twitter::Lite::Error->new(twitter_error => $obj, http_response => $res);
    }

    return $obj if $res->is_success && defined $obj;

    my $error = Net::Twitter::Lite::Error->new(http_response => $res);
    $error->twitter_error($obj) if ref $obj;

    die $error;
}

1;
