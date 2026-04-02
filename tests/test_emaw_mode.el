;;; test_emaw_mode.el --- ERT tests for emaw-mode.el

(require 'ert)

;; Load the generated emaw-mode.el instead of requiring from load-path
;; This gets invoked by pytest which can set the path dynamically,
;; but for now let's assume it gets loaded manually or we can load it here 
;; if we know the path. When invoked from pytest, the wrapper will load the generated file first.
;; So we just assume 'emaw-mode is available.

(ert-deftest emaw-mode-test-feature-provided ()
  "Test that emaw-mode provides its feature."
  (should (featurep 'emaw-mode)))

(ert-deftest emaw-mode-test-commands-exist ()
  "Test that the interactive commands are defined."
  (should (fboundp 'emaw-doctor))
  (should (commandp 'emaw-doctor))
  (should (fboundp 'emaw-init))
  (should (commandp 'emaw-init)))

(ert-deftest emaw-mode-test-keymap ()
  "Test that the keymap is bound correctly."
  (should (boundp 'emaw-mode-map))
  (should (keymapp emaw-mode-map))
  ;; Check that our keys are bound in the map
  (should (eq (lookup-key emaw-mode-map (kbd "C-c C-e d")) 'emaw-doctor))
  (should (eq (lookup-key emaw-mode-map (kbd "C-c C-e i")) 'emaw-init)))

(provide 'test_emaw_mode)
;;; test_emaw_mode.el ends here
