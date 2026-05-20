import os

base_dir = r"c:\Users\Expert Info\Desktop\Test_Project\smart_hydration_app\lib"

structure = {
    "core/constants/api_urls.dart": "class ApiUrls {\n  static const String baseUrl = 'http://127.0.0.1:8000/api/';\n}\n",
    "core/constants/app_colors.dart": "import 'package:flutter/material.dart';\n\nclass AppColors {\n  static const Color primary = Colors.blue;\n}\n",
    "core/constants/app_strings.dart": "class AppStrings {\n  static const String appName = 'Smart Hydration';\n}\n",
    "core/services/api_service.dart": "class ApiService {\n  // TODO: Implement API requests\n}\n",
    "core/services/storage_service.dart": "class StorageService {\n  // TODO: Implement local storage\n}\n",
    "core/services/bluetooth_service.dart": "class BluetoothService {\n  // TODO: Implement bluetooth scanning and connection\n}\n",
    "core/utils/validators.dart": "class Validators {\n  // TODO: Add input validation methods\n}\n",
    "core/utils/helpers.dart": "class Helpers {\n  // TODO: Add general helper functions\n}\n",
    "models/user_model.dart": "class UserModel {\n  // TODO: Define user fields based on backend\n}\n",
    "models/hydration_model.dart": "class HydrationModel {\n  // TODO: Define hydration session fields\n}\n",
    "models/skin_model.dart": "class SkinModel {\n  // TODO: Define skin record fields\n}\n",
    "models/final_status_model.dart": "class FinalStatusModel {\n  // TODO: Define final combined status fields\n}\n",
    "features/splash/splash_screen.dart": "import 'package:flutter/material.dart';\n\nclass SplashScreen extends StatelessWidget {\n  const SplashScreen({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Scaffold(\n      body: Center(child: Text('Splash Screen Placeholder')),\n    );\n  }\n}\n",
    "features/auth/login_screen.dart": "import 'package:flutter/material.dart';\n\nclass LoginScreen extends StatelessWidget {\n  const LoginScreen({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Scaffold(\n      body: Center(child: Text('Login Screen Placeholder')),\n    );\n  }\n}\n",
    "features/auth/register_screen.dart": "import 'package:flutter/material.dart';\n\nclass RegisterScreen extends StatelessWidget {\n  const RegisterScreen({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Scaffold(\n      body: Center(child: Text('Register Screen Placeholder')),\n    );\n  }\n}\n",
    "features/auth/auth_controller.dart": "import 'package:flutter/material.dart';\n\nclass AuthController extends ChangeNotifier {\n  // TODO: Add auth state, login/register methods\n}\n",
    "features/home/home_screen.dart": "import 'package:flutter/material.dart';\n\nclass HomeScreen extends StatelessWidget {\n  const HomeScreen({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Scaffold(\n      body: Center(child: Text('Home Screen Placeholder')),\n    );\n  }\n}\n",
    "features/home/home_controller.dart": "import 'package:flutter/material.dart';\n\nclass HomeController extends ChangeNotifier {\n  // TODO: Fetch dashboard data\n}\n",
    "features/home/widgets/water_card.dart": "import 'package:flutter/material.dart';\n\nclass WaterCard extends StatelessWidget {\n  const WaterCard({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Card(child: Padding(padding: EdgeInsets.all(8.0), child: Text('Water Card')));\n  }\n}\n",
    "features/home/widgets/status_card.dart": "import 'package:flutter/material.dart';\n\nclass StatusCard extends StatelessWidget {\n  const StatusCard({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Card(child: Padding(padding: EdgeInsets.all(8.0), child: Text('Status Card')));\n  }\n}\n",
    "features/home/widgets/advice_card.dart": "import 'package:flutter/material.dart';\n\nclass AdviceCard extends StatelessWidget {\n  const AdviceCard({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Card(child: Padding(padding: EdgeInsets.all(8.0), child: Text('Advice Card')));\n  }\n}\n",
    "features/hydration/add_water_screen.dart": "import 'package:flutter/material.dart';\n\nclass AddWaterScreen extends StatelessWidget {\n  const AddWaterScreen({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Scaffold(\n      body: Center(child: Text('Add Water Screen Placeholder')),\n    );\n  }\n}\n",
    "features/hydration/hydration_history_screen.dart": "import 'package:flutter/material.dart';\n\nclass HydrationHistoryScreen extends StatelessWidget {\n  const HydrationHistoryScreen({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Scaffold(\n      body: Center(child: Text('Hydration History Screen Placeholder')),\n    );\n  }\n}\n",
    "features/hydration/hydration_controller.dart": "import 'package:flutter/material.dart';\n\nclass HydrationController extends ChangeNotifier {\n  // TODO: Add water logging logic\n}\n",
    "features/bracelet/bracelet_screen.dart": "import 'package:flutter/material.dart';\n\nclass BraceletScreen extends StatelessWidget {\n  const BraceletScreen({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Scaffold(\n      body: Center(child: Text('Bracelet Screen Placeholder')),\n    );\n  }\n}\n",
    "features/bracelet/bracelet_controller.dart": "import 'package:flutter/material.dart';\n\nclass BraceletController extends ChangeNotifier {\n  // TODO: Bluetooth connection logic\n}\n",
    "features/history/history_screen.dart": "import 'package:flutter/material.dart';\n\nclass HistoryScreen extends StatelessWidget {\n  const HistoryScreen({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Scaffold(\n      body: Center(child: Text('History Screen Placeholder')),\n    );\n  }\n}\n",
    "features/settings/settings_screen.dart": "import 'package:flutter/material.dart';\n\nclass SettingsScreen extends StatelessWidget {\n  const SettingsScreen({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Scaffold(\n      body: Center(child: Text('Settings Screen Placeholder')),\n    );\n  }\n}\n",
    "features/settings/settings_controller.dart": "import 'package:flutter/material.dart';\n\nclass SettingsController extends ChangeNotifier {\n  // TODO: Update profile, logout logic\n}\n",
    "widgets/custom_button.dart": "import 'package:flutter/material.dart';\n\nclass CustomButton extends StatelessWidget {\n  final String text;\n  final VoidCallback onPressed;\n  const CustomButton({super.key, required this.text, required this.onPressed});\n\n  @override\n  Widget build(BuildContext context) {\n    return ElevatedButton(onPressed: onPressed, child: Text(text));\n  }\n}\n",
    "widgets/custom_textfield.dart": "import 'package:flutter/material.dart';\n\nclass CustomTextfield extends StatelessWidget {\n  final String hint;\n  const CustomTextfield({super.key, required this.hint});\n\n  @override\n  Widget build(BuildContext context) {\n    return TextField(decoration: InputDecoration(hintText: hint));\n  }\n}\n",
    "widgets/loading_widget.dart": "import 'package:flutter/material.dart';\n\nclass LoadingWidget extends StatelessWidget {\n  const LoadingWidget({super.key});\n\n  @override\n  Widget build(BuildContext context) {\n    return const Center(child: CircularProgressIndicator());\n  }\n}\n",
    "main.dart": '''import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'features/auth/auth_controller.dart';
import 'features/home/home_controller.dart';
import 'features/hydration/hydration_controller.dart';
import 'features/bracelet/bracelet_controller.dart';
import 'features/settings/settings_controller.dart';
import 'features/splash/splash_screen.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthController()),
        ChangeNotifierProvider(create: (_) => HomeController()),
        ChangeNotifierProvider(create: (_) => HydrationController()),
        ChangeNotifierProvider(create: (_) => BraceletController()),
        ChangeNotifierProvider(create: (_) => SettingsController()),
      ],
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Hydration',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const SplashScreen(),
    );
  }
}
'''
}

for filepath, content in structure.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

print(f"Flutter structure created successfully at: {base_dir}")
