// API_BASE_URL must be supplied via --dart-define at build/run time.
// Example:
//   flutter run --dart-define=API_BASE_URL=http://localhost/api
//   flutter build apk --dart-define=API_BASE_URL=https://api.example.com
//
// Never hard-code a URL in this file or anywhere else in the app.
class AppConfig {
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: '',
  );

  static void validate() {
    assert(
      apiBaseUrl.isNotEmpty,
      'API_BASE_URL is required. '
      'Pass --dart-define=API_BASE_URL=<url> when building or running.',
    );
  }
}
