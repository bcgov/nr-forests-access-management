/*
	This is the Geb configuration file.
	
	See: http://www.gebish.org/manual/current/#configuration
*/

import org.openqa.selenium.Dimension
import org.openqa.selenium.chrome.ChromeDriver
import org.openqa.selenium.chrome.ChromeOptions
import org.openqa.selenium.firefox.FirefoxDriver
import org.openqa.selenium.firefox.FirefoxOptions
import org.openqa.selenium.ie.InternetExplorerDriver
import org.openqa.selenium.edge.EdgeDriver
import org.openqa.selenium.safari.SafariDriver
import org.openqa.selenium.remote.DesiredCapabilities

waiting {
	timeout = 20
	retryInterval = 1
}

atCheckWaiting = [20, 1]

environments {
	
	// run via “./gradlew chromeTest”
	// See: https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver
	chrome {
				driver = { 
			//	def capabilities = org.openqa.selenium.remote.DesiredCapabilities.chrome()	
			//	capabilities.setCapability("PageLoadStrategy","normal")
			ChromeOptions o = new ChromeOptions()

			o.addArguments('--allow-running-insecure-content')
			o.addArguments('--allow-insecure-localhost')	
			o.setExperimentalOption('useAutomationExtension', false)
			o.addArguments('--safebrowsing-disable-download-protection')

			Map<String, Object> prefs = new HashMap<String, Object>()
			prefs.put('download.default_directory', downloadDir)
			prefs.put('safebrowsing.enabled', false)
			prefs.put('download.extensions_to_open', 'cfg')
			prefs.put('download.prompt_for_download', false)
			o.setExperimentalOption('prefs', prefs)
     	
			new ChromeDriver(o)

		}
	}








	// run via “./gradlew chromeHeadlessTest”
	// See: https://github.com/SeleniumHQ/selenium/wiki/ChromeDriver
	chromeHeadless {
		driver = {
			ChromeOptions o = new ChromeOptions()
			o.addArguments('headless')
			//o.addArguments('disable-gpu') 
			//o.addArguments('no-sandbox')
			o.addArguments('window-size=1980,1080')
			new ChromeDriver(o)
		}
	}
	
	// run via “./gradlew firefoxTest”
	// See: https://github.com/SeleniumHQ/selenium/wiki/FirefoxDriver
	// See also https://www.guru99.com/gecko-marionette-driver-selenium.html


	firefox {
		driver = { new FirefoxDriver() }
	}
		
	firefoxHeadless {
		driver = {
			FirefoxOptions o = new FirefoxOptions()
			o.addArguments("-headless")
			new FirefoxDriver(o)
		}
	}
/*	
	// run via “./gradlew ieTest”
	// See: https://github.com/SeleniumHQ/selenium/wiki/InternetExplorerDriver
	ie {
		def d = new DesiredCapabilities();
		d.setCapability(InternetExplorerDriver.INTRODUCE_FLAKINESS_BY_IGNORING_SECURITY_DOMAINS,true);
		d.setCapability(InternetExplorerDriver.IGNORE_ZOOM_SETTING,true);
		d.setCapability(InternetExplorerDriver.NATIVE_EVENTS,false);
		d.setCapability(InternetExplorerDriver.REQUIRE_WINDOW_FOCUS,true);
		
		driver = { new InternetExplorerDriver(d) }	
	}

	// run via “./gradlew edgeTest”
	// See: https://github.com/SeleniumHQ/selenium/wiki
	edge {
		driver = { new EdgeDriver() }
	}

	// run via “./gradlew safariTest”
	// See: https://github.com/SeleniumHQ/selenium/wiki
	safari {
		driver = { new SafariDriver() }
	}
*/	
}

// To run the tests with all browsers just run “./gradlew test”

baseNavigatorWaiting = true

// Allows for setting you baseurl in an environment variable.
// This is particularly handy for development and the pipeline
def env = System.getenv()
baseUrl = env['BASEURL']
if (!baseUrl) {
	//baseUrl = "https://startup-sample-project.td5cou-dev.nimbus.cloud.gov.bc.ca/"
      baseUrl = "http://localhost:4000/"
}

println "BaseURL: ${baseUrl}"
println "--------------------------"

cacheDriverPerThread = true
quitCachedDriverOnShutdown = true 

