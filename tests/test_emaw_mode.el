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
  (should (commandp 'emaw-init))
  (should (fboundp 'emaw-sync))
  (should (commandp 'emaw-sync))
  (should (fboundp 'emaw-task-run-tests))
  (should (commandp 'emaw-task-run-tests))
  ;; Internal helpers
  (should (fboundp 'emaw--task-sentinel))
  (should (fboundp 'emaw--run-task)))

(ert-deftest emaw-mode-test-keymap ()
  "Test that the keymap is bound correctly."
  (should (boundp 'emaw-mode-map))
  (should (keymapp emaw-mode-map))
  ;; Check that our keys are bound in the map
  (should (eq (lookup-key emaw-mode-map (kbd "C-c C-e d")) 'emaw-doctor))
  (should (eq (lookup-key emaw-mode-map (kbd "C-c C-e i")) 'emaw-init))
  (should (eq (lookup-key emaw-mode-map (kbd "C-c C-e s")) 'emaw-sync))
  (should (eq (lookup-key emaw-mode-map (kbd "C-c C-e t 1")) 'emaw-task-run-tests)))

(ert-deftest emaw-sentinel-sets-status-on-success ()
  "Sentinel sets emaw--last-task-status to SUCCESS when output contains [SUCCESS]."
  (let ((buf (generate-new-buffer "*emaw-test-sentinel*")))
    (unwind-protect
        (progn
          (with-current-buffer buf
            (insert "Some output\nemaw: task run-tests [SUCCESS]\n"))
          ;; Call sentinel directly — no real process needed.
          ;; We pass a dummy proc whose buffer is `buf'.
          (let ((fake-proc (start-process "emaw-test-dummy" buf "true")))
            (while (process-live-p fake-proc) (sleep-for 0.05))
            (emaw--task-sentinel fake-proc "finished\n" "run-tests"))
          (should (equal emaw--last-task-status "run-tests [SUCCESS]")))
      (kill-buffer buf))))

(ert-deftest emaw-sentinel-sets-status-on-failure ()
  "Sentinel sets emaw--last-task-status to FAILED when output contains [FAILED]."
  (let ((buf (generate-new-buffer "*emaw-test-sentinel-fail*")))
    (unwind-protect
        (progn
          (with-current-buffer buf
            (insert "Some output\nemaw: task run-tests [FAILED] (exit code 1)\n"))
          (let ((fake-proc (start-process "emaw-test-dummy-fail" buf "true")))
            (while (process-live-p fake-proc) (sleep-for 0.05))
            (emaw--task-sentinel fake-proc "exited abnormally with code 1\n" "run-tests"))
          (should (equal emaw--last-task-status "run-tests [FAILED]")))
      (kill-buffer buf))))

(ert-deftest emaw-sentinel-defaults-to-failed-on-missing-marker ()
  "Sentinel defaults to FAILED when buffer contains neither SUCCESS nor FAILED marker."
  (let ((buf (generate-new-buffer "*emaw-test-sentinel-empty*")))
    (unwind-protect
        (progn
          (with-current-buffer buf
            (insert "Process exited\n"))
          (let ((fake-proc (start-process "emaw-test-dummy-empty" buf "true")))
            (while (process-live-p fake-proc) (sleep-for 0.05))
            (emaw--task-sentinel fake-proc "finished\n" "lint-code"))
          (should (equal emaw--last-task-status "lint-code [FAILED]")))
      (kill-buffer buf))))

(provide 'test_emaw_mode)
;;; test_emaw_mode.el ends here
