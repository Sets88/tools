# Cookies

This is a method of storing information on the client side. Cookies are small text files that are sent by the browser to the server with each request. Cookies are stored in the browser and can be used by both the server and the client.

The browser typically transmits cookies in the Cookie header, and the server can send cookies in the Set-Cookie header.
Example:

    Cookie: test_cookie1=value; test_cookie2=123

    Set-Cookie: test_cookie1=value; Path=/; Domain=test.domain.com; Expires=Tue, 1 Jan 2025 00:00:00 GMT; HttpOnly; Secure; SameSite=None   

In this case, the flags HttpOnly, Secure, SameSite are also used.

## HttpOnly

The HttpOnly flag prohibits access to cookies from JavaScript. The cookie is transmitted by the browser itself.

## Secure

The Secure flag prohibits the transmission of cookies over an unsecured connection (http). The cookie is transmitted only over https.

## SameSite

The SameSite flag allows you to specify which requests can send cookies. Possible values: None, Lax, Strict

Lax - cookies are sent only when following a link
Strict - cookies are sent only when following a link and only to the domain from which the cookie was set
None - cookies are sent when following a link or when making requests through iframe, img src, etc.