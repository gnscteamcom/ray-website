package Net::Twitter::Lite::Error;
use warnings;
use strict;

use overload '""' => \&error;

sub new {
    my ($class, %args) = @_;

    return bless \%args, $class;
}

=item twitter_error

Get or set the encapsulated Twitter API error HASH ref.

=cut

sub twitter_error {
    my $self = shift;

    $self->{twitter_error} = shift if @_;

    return $self->{twitter_error};
}

=item http_response

Get or set the encapsulated HTTP::Response instance.

=cut

sub http_response {
    my $self = shift;

    $self->{http_response} = shift if @_;

    return $self->{http_response};
}

=item code

Returns the HTTP Status Code from the encapsulated HTTP::Response

=cut

sub code {
    my $self = shift;

    return exists $self->{http_response} && $self->{http_response}->code;
}

sub message {
    my $self = shift;

    return exists $self->{http_response} && $self->{http_response}->message;
}

sub error {
    my $self = shift;

    # We MUST stringyfy to something that evaluates to true, or testing $@ will fail!
    exists $self->{twitter_error} && $self->{twitter_error}{error}
        || ( exists $self->{http_response}
             && ($self->code . ": " . $self->message )
           )
        || '[unknown]';
}

1;

