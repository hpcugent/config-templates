structure template struct/basic_ssl;

"options" = list("-OptRenegotiate", "+StrictRequire", "+StdEnvVars");
"engine" = true;
"ciphersuite" = list("TLSv1");
"certificatefile" = value("/software/components/ccm/cert_file");
"certificatekeyfile" = value("/software/components/ccm/key_file");
"cacertificatefile" = value("/software/components/ccm/ca_file");
