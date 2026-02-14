import 'package:flutter/material.dart';
import 'package:smartbez/presentation/screens/auth/login_page.dart';
import 'package:smartbez/presentation/screens/auth/register_page.dart';
import 'package:smartbez/presentation/screens/dashboard/cart_page.dart';
import 'package:smartbez/presentation/screens/dashboard/category_page.dart';
import 'package:smartbez/presentation/screens/dashboard/product_detail_page.dart';
import 'package:smartbez/presentation/screens/dashboard/product_list_page.dart';
import 'package:smartbez/presentation/screens/splash_screen.dart';
import 'package:smartbez/presentation/screens/dashboard/main_nav_wrapper.dart';

import 'package:firebase_core/firebase_core.dart';
import 'package:provider/provider.dart';
import 'firebase_options.dart';
import 'services/auth_provider.dart' as auth;
import 'services/cart_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform,
  );
  runApp(const SmartBizApp());
}

class SmartBizApp extends StatelessWidget {
  const SmartBizApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => auth.AuthProvider()),
        ChangeNotifierProvider(create: (_) => CartProvider()),
      ],
      child: MaterialApp(
        home: const SplashPage(),
        debugShowCheckedModeBanner: false,
        title: 'SmartBiz',
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: const Color(0xFF36454F),
            primary: const Color(0xFF36454F),
            secondary: const Color(0xFFFF6B35), // Orange accent
            brightness: Brightness.light,
          ),
          scaffoldBackgroundColor: const Color(0xFFF5F5F5),
          appBarTheme: const AppBarTheme(
            backgroundColor: Color(0xFF36454F),
            foregroundColor: Colors.white,
            elevation: 0,
          ),
          elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF36454F),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
              textStyle: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
          inputDecorationTheme: InputDecorationTheme(
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFE0E0E0)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFFE0E0E0)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: Color(0xFF36454F), width: 2),
            ),
            labelStyle: const TextStyle(color: Color(0xFF36454F)),
          ),
        ),

        // Define named routes
        routes: {
          '/login': (_) => const LoginPage(), 
          '/register': (_) => const RegisterPage(),
          '/home': (_) => const MainNavWrapper(),
          '/categories': (_) => const CategoryPage(),
          '/products': (_) => const ProductListPage(),
          '/product_detail': (_) => const ProductDetailPage(),
          '/cart': (_) => const CartPage(),
        },
      ),
    );
  }
}
